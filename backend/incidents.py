"""Incident-based alert management for camera health failures."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from alerts import send_telegram_message, telegram_configured
from config import TELEGRAM_BOT_TOKEN
from database import connect, row_to_dict
from diagnosis_engine import diagnose_camera

ACTIVE_STATUSES = ("NEW", "NOTIFIED", "ACKNOWLEDGED", "IN_PROGRESS")
FIRST_REMINDER_HOURS = 6
REMINDER_INTERVAL_HOURS = 3


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def _active_placeholders():
    return ",".join("?" for _ in ACTIVE_STATUSES)


def _is_camera_in_maintenance(db, camera_id):
    camera = db.execute("SELECT id, switch_id FROM cameras WHERE id = ?", (camera_id,)).fetchone()
    if not camera:
        return False
    row = db.execute(
        """
        SELECT id, expected_end_time FROM maintenance_sessions
        WHERE maintenance_status = 'ACTIVE'
          AND (camera_id = ? OR (asset_type = 'CAMERA' AND COALESCE(asset_id, CAST(camera_id AS TEXT)) = ?))
        ORDER BY start_time DESC LIMIT 1
        """,
        (camera_id, str(camera_id)),
    ).fetchone()
    if not row and camera["switch_id"]:
        row = db.execute(
            """
            SELECT id, expected_end_time FROM maintenance_sessions
            WHERE maintenance_status = 'ACTIVE' AND asset_type = 'SWITCH' AND asset_id = ?
            ORDER BY start_time DESC LIMIT 1
            """,
            (camera["switch_id"],),
        ).fetchone()
    if not row:
        return False
    expected = row["expected_end_time"]
    if expected and expected <= now_text():
        completed = now_text()
        db.execute(
            """
            UPDATE maintenance_sessions
            SET maintenance_status = 'COMPLETED', completion_time = ?, notes = COALESCE(notes, '') || ' | Auto-restored after expected end time.'
            WHERE id = ?
            """,
            (completed, row["id"]),
        )
        db.execute(
            "INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)",
            ("MAINTENANCE_AUTO_RESTORED", f"Maintenance session {row['id']} expired and normal incident handling resumed.", completed),
        )
        return False
    return True


class IncidentRepository:
    def get_active_for_camera(self, db, camera_id):
        row = db.execute(
            f"SELECT * FROM incidents WHERE camera_id = ? AND status IN ({_active_placeholders()}) ORDER BY first_detected DESC LIMIT 1",
            (camera_id, *ACTIVE_STATUSES),
        ).fetchone()
        return row_to_dict(row) if row else None

    def get_incident(self, db, incident_id):
        row = db.execute("SELECT * FROM incidents WHERE incident_id = ?", (incident_id,)).fetchone()
        return row_to_dict(row) if row else None

    def create(self, db, camera, diagnosis, detected_at):
        next_notification = (datetime.fromisoformat(detected_at) + timedelta(hours=FIRST_REMINDER_HOURS)).isoformat(timespec="seconds")
        cursor = db.execute(
            """
            INSERT INTO incidents
            (camera_id, camera_name, severity, status, diagnosis, confidence, recommendation,
             first_detected, last_notification, next_notification, notification_count,
             acknowledged, acknowledged_by, acknowledged_time, resolved_time, downtime)
            VALUES (?, ?, ?, 'NEW', ?, ?, ?, ?, NULL, ?, 0, 0, NULL, NULL, NULL, NULL)
            """,
            (camera["id"], camera["name"], diagnosis["severity"], diagnosis["diagnosis"], diagnosis["confidence"], diagnosis["recommended_solution"], detected_at, next_notification),
        )
        incident_id = cursor.lastrowid
        self.log_transition(db, incident_id, None, "NEW", "Incident created after camera health failure detection.", detected_at)
        return self.get_incident(db, incident_id)

    def mark_notified(self, db, incident_id, status, notified_at, count, next_notification):
        db.execute(
            """
            UPDATE incidents
            SET status = ?, last_notification = ?, notification_count = ?, next_notification = ?
            WHERE incident_id = ?
            """,
            (status, notified_at, count, next_notification, incident_id),
        )

    def acknowledge(self, db, incident_id, user_label, acknowledged_at):
        incident = self.get_incident(db, incident_id)
        if not incident:
            return None
        old_status = incident["status"]
        db.execute(
            """
            UPDATE incidents
            SET acknowledged = 1, acknowledged_by = ?, acknowledged_time = ?, status = 'ACKNOWLEDGED'
            WHERE incident_id = ? AND status != 'RESOLVED'
            """,
            (user_label, acknowledged_at, incident_id),
        )
        if old_status != "ACKNOWLEDGED":
            self.log_transition(db, incident_id, old_status, "ACKNOWLEDGED", f"Incident acknowledged by {user_label}.", acknowledged_at)
        return self.get_incident(db, incident_id)

    def mark_in_progress(self, db, incident_id, user_label, started_at):
        incident = self.get_incident(db, incident_id)
        if not incident:
            return None
        old_status = incident["status"]
        db.execute(
            "UPDATE incidents SET status = 'IN_PROGRESS' WHERE incident_id = ? AND status NOT IN ('RESOLVED', 'CLOSED')",
            (incident_id,),
        )
        if old_status != "IN_PROGRESS":
            self.log_transition(db, incident_id, old_status, "IN_PROGRESS", f"Incident work started by {user_label}.", started_at)
        return self.get_incident(db, incident_id)

    def resolve(self, db, incident, resolved_at):
        first_detected = datetime.fromisoformat(incident["first_detected"])
        downtime = int((datetime.fromisoformat(resolved_at) - first_detected).total_seconds() // 60)
        old_status = incident["status"]
        db.execute(
            """
            UPDATE incidents
            SET status = 'RESOLVED', resolved_time = ?, downtime = ?, next_notification = NULL
            WHERE incident_id = ?
            """,
            (resolved_at, downtime, incident["incident_id"]),
        )
        self.log_transition(db, incident["incident_id"], old_status, "RESOLVED", "Camera recovered and incident was resolved automatically.", resolved_at)
        return downtime

    def due_reminders(self, db, due_at):
        rows = db.execute(
            f"""
            SELECT i.*, c.location, c.status AS camera_status
            FROM incidents i JOIN cameras c ON c.id = i.camera_id
            WHERE i.status IN ({_active_placeholders()})
              AND c.status != 'ONLINE'
              AND i.next_notification IS NOT NULL
              AND i.next_notification <= ?
            ORDER BY i.next_notification
            """,
            (*ACTIVE_STATUSES, due_at),
        ).fetchall()
        return [row_to_dict(row) for row in rows if not _is_camera_in_maintenance(db, row["camera_id"])]

    def log_transition(self, db, incident_id, from_status, to_status, description, created_at):
        db.execute(
            "INSERT INTO incident_state_log (incident_id, from_status, to_status, description, created_at) VALUES (?, ?, ?, ?, ?)",
            (incident_id, from_status, to_status, description, created_at),
        )
        db.execute(
            "INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)",
            ("INCIDENT_STATE_CHANGE", f"Incident {incident_id}: {from_status or 'NONE'} -> {to_status}. {description}", created_at),
        )

    def record_notification(self, db, incident, notification_type, recipient, delivery, sent_at, reminder_number=0):
        response = delivery.get("telegram_response") if isinstance(delivery, dict) else None
        message_id = None
        if isinstance(response, dict):
            message_id = (response.get("result") or {}).get("message_id")
        status = "DELIVERED" if delivery.get("sent") else "SKIPPED"
        result = delivery.get("reason") or delivery.get("channel") or "Notification event recorded"
        db.execute(
            """
            INSERT INTO incident_notifications
            (incident_id, notification_type, recipient, sent_time, delivery_status, delivery_result, reminder_number, telegram_message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (incident["incident_id"], notification_type, recipient, sent_at, status, result, reminder_number, message_id),
        )
        db.execute(
            """
            INSERT INTO notification_history
            (notification_type, recipient, status, delivery_result, camera_id, camera_name, severity, diagnosis, confidence, recommended_action, resolution_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (notification_type, recipient, status, result, incident["camera_id"], incident["camera_name"], incident["severity"], incident["diagnosis"], incident["confidence"], incident["recommendation"], incident["status"], sent_at),
        )


class TelegramIncidentService:
    def send_incident(self, incident, location, kind):
        camera = self._camera_for_incident(incident)
        message = self._initial_alert_message(incident, camera or {"location": location}, kind)
        markup = {"inline_keyboard": [[
            {"text": "Acknowledge", "callback_data": f"ack:{incident['incident_id']}"},
            {"text": "In Progress", "callback_data": f"progress:{incident['incident_id']}"},
            {"text": "View Incident", "callback_data": f"view:{incident['incident_id']}"},
        ]]}
        return send_telegram_message(message, reply_markup=markup)

    def send_restored(self, incident, camera, downtime):
        message = "\n".join([
            "CAMERA RECOVERED", "", "Camera", incident["camera_name"], "", "Location",
            camera.get("location") or "Not specified", "", "Status", "RESOLVED", "",
            "Total Downtime", f"{downtime} minutes", "", now_text(), "", "Monitoring Status", "Healthy",
        ])
        return send_telegram_message(message)

    def poll_acknowledgements(self):
        if not telegram_configured():
            return {"ok": True, "processed": 0, "skipped": True}
        processed = 0
        with connect() as db:
            offset = self._state_get(db, "telegram_update_offset") or "0"
            data = self._telegram_api("getUpdates", {"timeout": 1, "offset": offset})
            repo = IncidentRepository()
            for update in data.get("result", []) if data.get("ok") else []:
                update_id = update.get("update_id")
                if update_id is not None:
                    self._state_set(db, "telegram_update_offset", str(update_id + 1))
                callback = update.get("callback_query") or {}
                payload = callback.get("data") or ""
                if not payload:
                    continue
                user = callback.get("from") or {}
                label = user.get("username") or user.get("first_name") or str(user.get("id") or "Telegram operator")
                callback_id = callback.get("id")
                action, incident_id = self._parse_callback(payload)
                if not incident_id:
                    continue
                if action == "ack":
                    incident = repo.acknowledge(db, incident_id, label, now_text())
                    self._send_operator_acknowledged(incident, label) if incident else None
                    self._answer_callback(callback_id, "Acknowledged" if incident else "Incident not found")
                    processed += 1
                elif action == "progress":
                    incident = repo.mark_in_progress(db, incident_id, label, now_text())
                    self._send_operator_in_progress(incident, label) if incident else None
                    self._answer_callback(callback_id, "Marked in progress" if incident else "Incident not found")
                    processed += 1
                elif action == "view":
                    incident = repo.get_incident(db, incident_id)
                    self._send_incident_report(db, incident) if incident else None
                    self._answer_callback(callback_id, "Incident report sent" if incident else "Incident not found")
                    processed += 1
        return {"ok": True, "processed": processed}

    def _initial_alert_message(self, incident, camera, kind):
        status_label = "REMINDER" if kind == "reminder" else "NEW"
        switch_name = camera.get("switch_id") or "Not mapped"
        switch_port = camera.get("switch_port") or "Port not mapped"
        return "\n".join([
            "CAMERA HEALTH ALERT", "", f"Severity: {self._title(incident.get('severity'))}", "", "Camera",
            incident["camera_name"], "", "Location", camera.get("location") or "Not specified", "", "Switch",
            f"{switch_name} ({switch_port})", "", "Probable Cause", incident.get("diagnosis") or "Under investigation",
            "", "Detected", self._display_time(incident.get("first_detected")), "", "Recommendation",
            self._first_recommendation(incident.get("recommendation")), "", "Status", status_label,
        ])

    def _send_operator_acknowledged(self, incident, username):
        return send_telegram_message("\n".join([
            "INCIDENT ACKNOWLEDGED", "", "Incident ID", str(incident["incident_id"]), "", "Camera",
            incident["camera_name"], "", "Acknowledged By", username, "", "Time",
            self._display_time(incident.get("acknowledged_time") or now_text()), "", "Status", "ACKNOWLEDGED",
        ]))

    def _send_operator_in_progress(self, incident, username):
        return send_telegram_message("\n".join([
            "INCIDENT UPDATE", "", "Incident ID", str(incident["incident_id"]), "", "Camera",
            incident["camera_name"], "", "Engineer", username, "", "Started", self._display_time(now_text()),
            "", "Status", "IN PROGRESS",
        ]))

    def _send_incident_report(self, db, incident):
        camera = self._camera_for_incident(incident, db) or {}
        latest_ping = self._latest_ping(db, incident["camera_id"])
        evidence = self._diagnosis_evidence(db, incident, camera, latest_ping)
        recommendations = self._recommendation_lines(incident.get("recommendation"))
        affected = self._affected_camera_count(db, camera.get("switch_id"))
        lines = [
            "INCIDENT REPORT", "--------------------", "Incident ID", str(incident["incident_id"]),
            "Severity", self._title(incident.get("severity")), "Current Status", incident.get("status") or "Unknown",
            "--------------------", "Camera Information", "Camera Name", incident["camera_name"], "Camera ID",
            str(incident["camera_id"]), "Location", camera.get("location") or "Not specified", "Building",
            camera.get("building") or camera.get("location") or "Not mapped", "Floor", camera.get("floor") or "Not mapped",
            "IP Address", camera.get("ip_address") or "Not available", "Switch Name", camera.get("switch_id") or "Not mapped",
            "Switch Port", camera.get("switch_port") or "Not mapped", "--------------------", "Current Health",
            "Health Score", f"{self._health_score(camera, latest_ping)}%", "Current Downtime", self._current_downtime(incident),
            "Last Heartbeat", self._display_time(camera.get("last_checked")), "--------------------", "AI Diagnosis",
            "Probable Cause", incident.get("diagnosis") or "Under investigation", "Confidence Score", f"{incident.get('confidence')}%",
            "--------------------", "Diagnosis Evidence", *evidence, "--------------------", "Business Impact",
            "Affected Area", camera.get("location") or "Not specified", "Affected Cameras", str(affected), "Recording Status",
            "Interrupted" if camera.get("status") in ("OFFLINE", "STREAM_FAILURE") else "At risk", "Monitoring Status",
            "MAINTENANCE" if camera.get("maintenance_status") == "ACTIVE" else (camera.get("status") or "Unknown"),
            "Priority", self._priority(incident.get("severity")), "--------------------", "Professional Recommendations",
            *recommendations, "--------------------", "Notification Information", "Notification Number",
            str(incident.get("notification_count") or 0), "Current Reminder", str(max(0, (incident.get("notification_count") or 1) - 1)),
            "Next Reminder", self._display_time(incident.get("next_notification")), "First Detection Time",
            self._display_time(incident.get("first_detected")),
        ]
        return send_telegram_message("\n".join(lines))

    def _camera_for_incident(self, incident, db=None):
        close_db = False
        if db is None:
            db_ctx = connect()
            db = db_ctx.__enter__()
            close_db = True
        try:
            row = db.execute("SELECT * FROM cameras WHERE id = ?", (incident["camera_id"],)).fetchone()
            return row_to_dict(row) if row else None
        finally:
            if close_db:
                db_ctx.__exit__(None, None, None)

    def _latest_ping(self, db, camera_id):
        row = db.execute("SELECT * FROM ping_history WHERE camera_id = ? ORDER BY recorded_at DESC LIMIT 1", (camera_id,)).fetchone()
        return row_to_dict(row) if row else {}

    def _diagnosis_evidence(self, db, incident, camera, latest_ping):
        evidence = []
        status = camera.get("status")
        stream = (camera.get("stream_status") or "").lower()
        packet_loss = latest_ping.get("packet_loss_pct")
        latency = latest_ping.get("response_time_ms") or camera.get("latency_ms")
        if status == "OFFLINE":
            evidence.extend(["Ping Timeout", "Camera Heartbeat Lost"])
        if status == "STREAM_FAILURE" or "rtsp" in stream:
            evidence.append("RTSP Connection Failed")
        if packet_loss is not None and packet_loss >= 100:
            evidence.append("Packet Loss 100%")
        elif packet_loss:
            evidence.append(f"Packet Loss {packet_loss}%")
        if latency and latency >= 150:
            evidence.append(f"High Latency {latency} ms")
        if camera.get("switch_ip"):
            evidence.append("Switch Reachable")
        if camera.get("switch_id"):
            row = db.execute("SELECT COUNT(*) AS total FROM cameras WHERE switch_id = ? AND id != ? AND status = 'ONLINE'", (camera.get("switch_id"), incident["camera_id"])).fetchone()
            if row and row["total"]:
                evidence.append("Other Cameras Online")
        return evidence or ["Health status changed based on ping, stream, or heartbeat checks"]

    def _recommendation_lines(self, recommendation):
        lines = []
        for raw in (recommendation or "").splitlines():
            item = raw.strip().lstrip("- ").strip()
            if item:
                lines.append(f"- {item}")
        return lines[:4] or ["- Review camera power, network path and RTSP service."]

    def _first_recommendation(self, recommendation):
        lines = self._recommendation_lines(recommendation)
        return lines[0].replace("- ", "", 1) if lines else "Review camera power, network path and RTSP service."

    def _health_score(self, camera, latest_ping):
        status = camera.get("status")
        if camera.get("maintenance_status") == "ACTIVE":
            return 75
        return {"ONLINE": 100, "UNSTABLE": 65, "STREAM_FAILURE": 45, "OFFLINE": 0}.get(status, 50)

    def _current_downtime(self, incident):
        start = incident.get("first_detected")
        if not start:
            return "Not available"
        end = incident.get("resolved_time") or now_text()
        minutes = int((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() // 60)
        if minutes < 60:
            return f"{minutes} minutes"
        hours, mins = divmod(minutes, 60)
        return f"{hours}h {mins}m"

    def _affected_camera_count(self, db, switch_id):
        if not switch_id:
            return 1
        row = db.execute("SELECT COUNT(*) AS total FROM cameras WHERE switch_id = ? AND status != 'ONLINE'", (switch_id,)).fetchone()
        return row["total"] if row else 1

    def _parse_callback(self, payload):
        if ":" not in payload:
            return payload, None
        action, raw_id = payload.split(":", 1)
        try:
            return action, int(raw_id)
        except ValueError:
            return action, None

    def _priority(self, severity):
        return {"CRITICAL": "Immediate", "HIGH": "High", "MEDIUM": "Medium", "LOW": "Routine"}.get(str(severity or "").upper(), "Medium")

    def _title(self, value):
        return str(value or "Unknown").replace("_", " ").title()

    def _display_time(self, value):
        if not value:
            return "Not scheduled"
        try:
            return datetime.fromisoformat(value).strftime("%d %b %Y, %I:%M %p")
        except Exception:
            return str(value)

    def _telegram_api(self, method, params):
        payload = urllib.parse.urlencode(params).encode("utf-8")
        request = urllib.request.Request(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}", data=payload, method="POST")
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    def _answer_callback(self, callback_id, text):
        if not callback_id:
            return
        try:
            self._telegram_api("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": "false"})
        except Exception:
            pass

    def _state_get(self, db, key):
        row = db.execute("SELECT value FROM incident_runtime_state WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def _state_set(self, db, key, value):
        db.execute(
            """
            INSERT INTO incident_runtime_state (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            """,
            (key, value, now_text()),
        )


class IncidentService:
    def __init__(self):
        self.repo = IncidentRepository()
        self.telegram = TelegramIncidentService()

    def handle_camera_failure(self, db, camera, health, diagnosis=None, detected_at=None):
        if _is_camera_in_maintenance(db, camera["id"]):
            return {"ok": True, "suppressed": True, "reason": "Camera is in maintenance mode"}
        detected_at = detected_at or now_text()
        diagnosis = diagnosis or diagnose_camera(camera, health)
        existing = self.repo.get_active_for_camera(db, camera["id"])
        if existing:
            return {"ok": True, "existing": True, "incident": existing}
        incident = self.repo.create(db, camera, diagnosis, detected_at)
        delivery = self.telegram.send_incident(incident, camera.get("location"), "new")
        next_notification = (datetime.fromisoformat(detected_at) + timedelta(hours=FIRST_REMINDER_HOURS)).isoformat(timespec="seconds")
        self.repo.mark_notified(db, incident["incident_id"], "NOTIFIED", detected_at, 1, next_notification)
        notified = self.repo.get_incident(db, incident["incident_id"])
        self.repo.record_notification(db, notified, "TELEGRAM", "Configured Telegram Chat", delivery, detected_at, 0)
        self.repo.log_transition(db, incident["incident_id"], "NEW", "NOTIFIED", "Initial incident notification sent to Telegram.", detected_at)
        return {"ok": True, "existing": False, "incident": notified, "delivery": delivery}

    def resolve_camera(self, db, camera, resolved_at=None):
        resolved_at = resolved_at or now_text()
        incident = self.repo.get_active_for_camera(db, camera["id"])
        if not incident:
            return {"ok": True, "resolved": False}
        downtime = self.repo.resolve(db, incident, resolved_at)
        delivery = self.telegram.send_restored(incident, camera, downtime)
        resolved = self.repo.get_incident(db, incident["incident_id"])
        self.repo.record_notification(db, resolved, "TELEGRAM", "Configured Telegram Chat", delivery, resolved_at, incident.get("notification_count") or 0)
        return {"ok": True, "resolved": True, "incident": resolved, "delivery": delivery}

    def send_due_reminders(self):
        due_at = now_text()
        sent = []
        with connect() as db:
            for incident in self.repo.due_reminders(db, due_at):
                count = int(incident.get("notification_count") or 0)
                reminder_number = max(1, count)
                next_notification = (datetime.fromisoformat(due_at) + timedelta(hours=REMINDER_INTERVAL_HOURS)).isoformat(timespec="seconds")
                new_status = incident["status"]
                if new_status == "NOTIFIED":
                    self.repo.log_transition(db, incident["incident_id"], "NOTIFIED", "IN_PROGRESS", "Reminder cycle started while camera remains unhealthy.", due_at)
                    new_status = "IN_PROGRESS"
                    incident["status"] = new_status
                delivery = self.telegram.send_incident(incident, incident.get("location"), "reminder")
                self.repo.mark_notified(db, incident["incident_id"], new_status, due_at, count + 1, next_notification)
                updated = self.repo.get_incident(db, incident["incident_id"])
                self.repo.record_notification(db, updated, "TELEGRAM", "Configured Telegram Chat", delivery, due_at, reminder_number)
                sent.append({"incident_id": incident["incident_id"], "reminder_number": reminder_number})
        return sent

    def synchronize_current_failures(self):
        created = []
        detected_at = now_text()
        with connect() as db:
            rows = db.execute("SELECT * FROM cameras WHERE status IN ('OFFLINE', 'STREAM_FAILURE', 'UNSTABLE') ORDER BY id").fetchall()
            for row in rows:
                camera = row_to_dict(row)
                health = {"status": camera["status"], "latency_ms": camera.get("latency_ms"), "packet_loss_pct": 100 if camera["status"] == "OFFLINE" else 0, "stream_status": camera.get("stream_status")}
                result = self.handle_camera_failure(db, camera, health, None, detected_at)
                if result.get("incident") and not result.get("existing"):
                    created.append(result["incident"]["incident_id"])
        return created

    def poll_telegram_acknowledgements(self):
        return self.telegram.poll_acknowledgements()


def get_incidents(status=None):
    with connect() as db:
        if status:
            rows = db.execute("SELECT * FROM incidents WHERE status = ? ORDER BY first_detected DESC", (status,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM incidents ORDER BY first_detected DESC LIMIT 500").fetchall()
    return [row_to_dict(row) for row in rows]


def get_incident_notifications(incident_id=None):
    with connect() as db:
        if incident_id:
            rows = db.execute("SELECT * FROM incident_notifications WHERE incident_id = ? ORDER BY sent_time DESC", (incident_id,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM incident_notifications ORDER BY sent_time DESC LIMIT 500").fetchall()
    return [row_to_dict(row) for row in rows]


def get_incident_state_log(incident_id=None):
    with connect() as db:
        if incident_id:
            rows = db.execute("SELECT * FROM incident_state_log WHERE incident_id = ? ORDER BY created_at DESC", (incident_id,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM incident_state_log ORDER BY created_at DESC LIMIT 500").fetchall()
    return [row_to_dict(row) for row in rows]


def get_incident_summary():
    today = datetime.now().date().isoformat()
    with connect() as db:
        active_rows = [row_to_dict(row) for row in db.execute("SELECT severity, status FROM incidents WHERE status IN ('NEW', 'NOTIFIED', 'ACKNOWLEDGED', 'IN_PROGRESS')").fetchall()]
        resolved = db.execute("SELECT downtime FROM incidents WHERE status = 'RESOLVED' AND resolved_time LIKE ?", (today + "%",)).fetchall()
    downtime_values = [row["downtime"] for row in resolved if row["downtime"] is not None]
    return {
        "active_incidents": len(active_rows),
        "critical_incidents": sum(1 for item in active_rows if item["severity"] == "CRITICAL"),
        "high_incidents": sum(1 for item in active_rows if item["severity"] == "HIGH"),
        "acknowledged_incidents": sum(1 for item in active_rows if item["status"] == "ACKNOWLEDGED"),
        "in_progress": sum(1 for item in active_rows if item["status"] == "IN_PROGRESS"),
        "resolved_today": len(downtime_values),
        "average_resolution_time": round(sum(downtime_values) / len(downtime_values), 1) if downtime_values else None,
    }
