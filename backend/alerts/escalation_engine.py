"""Persistent staged escalation workflow for unresolved camera incidents."""

from datetime import datetime, timedelta

from alerts import send_email_report, send_telegram_message
from alert_rules import (
    ALERT_TYPES,
    CAMERA_FAILURE,
    STAGE_2_DELAY_MINUTES,
    STAGE_3_DELAY_MINUTES,
    STAGE_4_DELAY_MINUTES,
)
from database import connect, row_to_dict


class EscalationEngine:
    """Create, advance and resolve camera escalation records."""

    def trigger(self, camera_id, alert_type=CAMERA_FAILURE):
        if alert_type not in ALERT_TYPES:
            alert_type = CAMERA_FAILURE
        with connect() as db:
            camera = db.execute("SELECT name, status, stream_status FROM cameras WHERE id = ?", (camera_id,)).fetchone()
            if not camera:
                return {"ok": False, "reason": "Camera not found"}
            active = db.execute(
                "SELECT id FROM escalations WHERE camera_id = ? AND alert_type = ? AND status = 'ACTIVE' LIMIT 1",
                (camera_id, alert_type),
            ).fetchone()
            if active:
                return {"ok": True, "escalation_id": active["id"], "existing": True}
            now = datetime.now().isoformat(timespec="seconds")
            cursor = db.execute(
                """
                INSERT INTO escalations (camera_id, camera_name, alert_type, stage, triggered_at, completed_at, status)
                VALUES (?, ?, ?, 1, ?, NULL, 'ACTIVE')
                """,
                (camera_id, camera["name"], alert_type, now),
            )
            escalation_id = cursor.lastrowid
        message = self._message("Stage 1", camera_id, camera["name"], alert_type, camera["status"], camera["stream_status"])
        send_telegram_message(message)
        return {"ok": True, "escalation_id": escalation_id, "existing": False}

    def advance_stages(self):
        now = datetime.now()
        advanced = []
        with connect() as db:
            rows = db.execute("SELECT * FROM escalations WHERE status = 'ACTIVE' ORDER BY triggered_at").fetchall()
            for row in rows:
                escalation = row_to_dict(row)
                triggered_at = datetime.fromisoformat(escalation["triggered_at"])
                stage = escalation["stage"]
                if now >= triggered_at + timedelta(minutes=STAGE_4_DELAY_MINUTES) and stage < 4:
                    self._send_stage(escalation, 4)
                    db.execute(
                        "UPDATE escalations SET stage = 4, status = 'ESCALATED', completed_at = ? WHERE id = ?",
                        (now.isoformat(timespec="seconds"), escalation["id"]),
                    )
                    advanced.append({"id": escalation["id"], "stage": 4})
                elif now >= triggered_at + timedelta(minutes=STAGE_3_DELAY_MINUTES) and stage < 3:
                    self._send_stage(escalation, 3)
                    db.execute("UPDATE escalations SET stage = 3 WHERE id = ?", (escalation["id"],))
                    advanced.append({"id": escalation["id"], "stage": 3})
                elif now >= triggered_at + timedelta(minutes=STAGE_2_DELAY_MINUTES) and stage < 2:
                    self._send_stage(escalation, 2)
                    db.execute("UPDATE escalations SET stage = 2 WHERE id = ?", (escalation["id"],))
                    advanced.append({"id": escalation["id"], "stage": 2})
        return advanced

    def resolve(self, camera_id):
        now = datetime.now().isoformat(timespec="seconds")
        with connect() as db:
            db.execute(
                "UPDATE escalations SET status = 'RESOLVED', completed_at = ? WHERE camera_id = ? AND status = 'ACTIVE'",
                (now, camera_id),
            )
        return {"ok": True, "camera_id": camera_id}

    def _send_stage(self, escalation, stage):
        label = f"Stage {stage}"
        message = self._message(label, escalation["camera_id"], escalation["camera_name"], escalation["alert_type"], "UNRESOLVED", "Escalation remains active")
        if stage == 2:
            send_email_report(f"UCEK-JNTUK Escalation Stage 2 - {escalation['camera_name']}", message)
        elif stage == 3:
            send_telegram_message(f"CRITICAL ESCALATION\n{message}")
        elif stage == 4:
            send_email_report(f"UCEK-JNTUK Admin Escalation - {escalation['camera_name']}", message)

    @staticmethod
    def _message(stage, camera_id, camera_name, alert_type, status, health):
        return "\n".join([
            "UCEK-JNTUK Camera Health Monitoring Escalation",
            stage,
            f"Camera: {camera_name} (ID {camera_id})",
            f"Alert Type: {alert_type}",
            f"Current Status: {status}",
            f"Health Detail: {health}",
            "Action: Review network path, camera power, switch port and RTSP stream availability.",
        ])
