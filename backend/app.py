import json
import logging
import platform
import sys
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from alerts import email_configured, send_email_report, send_telegram_message, telegram_configured
from config import ALLOWED_ORIGINS, BASE_DIR, DEMO_MODE, validate_runtime_secrets
from database import backup_database, connect, init_db, row_to_dict
from diagnosis_engine import diagnose_camera, recommendation_text, RECOMMENDATIONS
from monitoring.monitor_scheduler import MonitorScheduler
from monitoring.probe import probe_camera
from ml.model_scheduler import ModelTrainingScheduler
from ml.risk_engine import ensure_models, latest_predictions, run_all_predictions
from topology import get_topology_data
from analytics import get_camera_analytics, get_downtime_trend, get_system_summary
from reports import generate_csv_report
from auth import create_token, hash_password, require_auth, verify_password
from incidents import IncidentService, get_incident_notifications, get_incident_state_log, get_incident_summary, get_incidents
from maintenance_service import MaintenanceService
from enterprise_analytics import RootCauseAnalyticsService
from enterprise_reports import ReportService
from ai_feedback_service import AIFeedbackService
from switch_service import SwitchService

ALERT_ENGINE_DIR = Path(__file__).resolve().parent / "alerts"
if str(ALERT_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ALERT_ENGINE_DIR))
from alert_scheduler import AlertScheduler
from websocket.event_dispatcher import dispatch
from websocket.websocket_server import start_websocket_server


HOST = "127.0.0.1"
PORT = 8000
DIST_DIR = BASE_DIR / "dist"
MONITOR_STARTED = False
WEBSOCKET_STARTED = False
ALERT_SCHEDULER_STARTED = False
MODEL_SCHEDULER_STARTED = False
SCHEDULER = MonitorScheduler(interval_seconds=30)
ALERT_SCHEDULER = AlertScheduler()
MODEL_SCHEDULER = ModelTrainingScheduler()


def _apply_cors_headers(handler):
    origin = handler.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        handler.send_header("Access-Control-Allow-Origin", origin)
        handler.send_header("Vary", "Origin")
    elif not origin and ALLOWED_ORIGINS:
        handler.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGINS[0])
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    handler.send_header("Access-Control-Allow-Credentials", "true")


def json_response(handler, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    _apply_cors_headers(handler)
    handler.end_headers()
    handler.wfile.write(body)


def file_response(handler, body, content_type, filename):
    if isinstance(body, str):
        data = body.encode("utf-8")
    else:
        data = body
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Disposition", f'attachment; filename="{filename}"')
    handler.send_header("Content-Length", str(len(data)))
    _apply_cors_headers(handler)
    handler.end_headers()
    handler.wfile.write(data)


def report_response(handler, path, query):
    periods = {"/api/reports/daily": (1, "daily-report"), "/api/reports/weekly": (7, "weekly-report"), "/api/reports/monthly": (30, "monthly-report")}
    period_days, name = periods[path]
    file_response(handler, generate_csv_report(period_days), "text/csv; charset=utf-8", f"{name}.csv")


def read_body(handler, max_bytes=1_000_000):
    try:
        length = int(handler.headers.get("Content-Length", "0") or 0)
    except (TypeError, ValueError):
        raise ValueError("Invalid Content-Length header")
    if length > max_bytes:
        raise ValueError("Request body exceeds maximum allowed size (1MB)")
    if not length:
        return {}
    raw_data = handler.rfile.read(length)
    try:
        return json.loads(raw_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Request body must be valid JSON") from exc


RTSP_VISIBLE_ROLES = {"ADMINISTRATOR", "NETWORK_ENGINEER"}
PUBLIC_GET_PATHS = {"/api/health"}
PUBLIC_POST_PATHS = {"/api/auth/login", "/api/auth/logout"}
BLOCKED_STATIC_SUFFIXES = {".db", ".env", ".py", ".pyc", ".pem", ".key", ".ini"}


def check_camera_health(camera):
    return probe_camera(camera)


def normalize_probe_mode(value, fallback=""):
    raw = str(value if value is not None else fallback or "").strip().upper()
    if raw in ("", "LIVE", "SIMULATED"):
        return raw
    raise ValueError("probe_mode must be LIVE, SIMULATED, or empty")


def can_see_rtsp(user):
    return bool(user) and user.get("role") in RTSP_VISIBLE_ROLES


def sanitize_camera(camera, user):
    if not camera:
        return camera
    data = dict(camera)
    if not can_see_rtsp(user):
        data["rtsp_url"] = ""
    return data


def sanitize_cameras(cameras, user):
    return [sanitize_camera(camera, user) for camera in cameras]


def sanitize_switch(switch, user):
    if not switch:
        return switch
    data = dict(switch)
    if data.get("cameras"):
        data["cameras"] = sanitize_cameras(data["cameras"], user)
    return data


def monitor_runtime():
    return SCHEDULER.runtime_status()


def api_user(handler, path, method):
    if method == "GET" and path in PUBLIC_GET_PATHS:
        return {"role": None, "public": True}
    if method == "POST" and path in PUBLIC_POST_PATHS:
        return {"role": None, "public": True}
    if not path.startswith("/api/"):
        return None
    return require_auth(handler)


def get_cameras():
    with connect() as db:
        rows = db.execute("SELECT * FROM cameras ORDER BY id").fetchall()
        return [row_to_dict(row) for row in rows]


def get_camera(camera_id):
    with connect() as db:
        row = db.execute("SELECT * FROM cameras WHERE id = ?", (camera_id,)).fetchone()
        return row_to_dict(row) if row else None


def switch_stats():
    cameras = get_cameras()
    switches = {}
    for camera in cameras:
        key = camera["switch_id"]
        switches.setdefault(key, {"switch_id": key, "switch_ip": camera.get("switch_ip", ""), "total": 0, "offline": 0})
        switches[key]["total"] += 1
        if camera["status"] == "OFFLINE":
            switches[key]["offline"] += 1
    values = list(switches.values())
    return {
        "total": len(values),
        "online": sum(1 for item in values if item["offline"] < item["total"]),
        "offline": sum(1 for item in values if item["total"] and item["offline"] == item["total"]),
        "items": values,
    }


def get_stats():
    cameras = get_cameras()
    return {
        "total": len(cameras),
        "online": sum(1 for camera in cameras if camera["status"] == "ONLINE"),
        "offline": sum(1 for camera in cameras if camera["status"] == "OFFLINE"),
        "unstable": sum(1 for camera in cameras if camera["status"] == "UNSTABLE"),
        "stream_failure": sum(1 for camera in cameras if camera["status"] == "STREAM_FAILURE"),
        "switches": switch_stats(),
    }


def get_stream_status():
    with connect() as db:
        rows = db.execute(
            """
            SELECT id AS camera_id, name, status, stream_status, stream_response_ms, last_stream_check
            FROM cameras ORDER BY id
            """
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def log_activity(action, description):
    with connect() as db:
        db.execute(
            "INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)",
            (action, description, datetime.now().isoformat(timespec="seconds")),
        )


def get_user_activity():
    with connect() as db:
        rows = db.execute("SELECT * FROM user_activity ORDER BY created_at DESC LIMIT 200").fetchall()
        return [row_to_dict(row) for row in rows]


def get_settings():
    with connect() as db:
        row = db.execute("SELECT * FROM settings WHERE id = 1").fetchone()
        data = row_to_dict(row)
        if not data:
            return data
        data["email_recipients"] = ""
        data["telegram_bot_token"] = ""
        data["telegram_chat_id"] = ""
        data["notification_service"] = {
            "email_configured": email_configured(),
            "telegram_configured": telegram_configured(),
            "mode": "Automatic"
        }
        return data


def update_settings(body):
    with connect() as db:
        current = row_to_dict(db.execute("SELECT * FROM settings WHERE id = 1").fetchone()) or {}
        fields = {
            "user_name": body.get("user_name", current.get("user_name", "UCEK-JNTUK Admin")),
            "user_role": body.get("user_role", current.get("user_role", "Campus Surveillance Administrator")),
            "user_email": body.get("user_email", current.get("user_email", "")),
            "email_recipients": body.get("email_recipients", current.get("email_recipients", "")),
            "telegram_bot_token": body.get("telegram_bot_token", current.get("telegram_bot_token", "")),
            "telegram_chat_id": body.get("telegram_chat_id", current.get("telegram_chat_id", "")),
        }
        db.execute(
            """
            UPDATE settings
            SET user_name = ?, user_role = ?, user_email = ?, email_recipients = ?,
                telegram_bot_token = ?, telegram_chat_id = ?, updated_at = ?
            WHERE id = 1
            """,
            (*fields.values(), datetime.now().isoformat(timespec="seconds")),
        )
    log_activity("SETTINGS_UPDATED", "User and notification settings were updated.")
    return get_settings()


def create_camera(body):
    required = ["name", "location", "ip_address", "switch_id", "switch_ip", "rtsp_url"]
    missing = [field for field in required if not body.get(field)]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    probe_mode = normalize_probe_mode(body.get("probe_mode"), "")
    now = datetime.now().isoformat(timespec="seconds")
    health = check_camera_health({
        "ip_address": body["ip_address"],
        "rtsp_url": body["rtsp_url"],
        "probe_mode": probe_mode,
        "status": None,
        "id": 0,
    })
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO cameras
            (name, location, ip_address, switch_id, switch_ip, rtsp_url, probe_mode, status, last_checked,
             latency_ms, stream_status, stream_response_ms, last_stream_check)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                body["name"], body["location"], body["ip_address"], body["switch_id"], body["switch_ip"],
                body["rtsp_url"], probe_mode, health["status"], now, health["latency_ms"], health["stream_status"],
                health["stream_response_ms"], now,
            ),
        )
        camera_id = cursor.lastrowid
        db.execute(
            """
            INSERT INTO ping_history (camera_id, response_time_ms, packet_loss_pct, recorded_at, is_anomaly)
            VALUES (?, ?, ?, ?, ?)
            """,
            (camera_id, health["latency_ms"], health["packet_loss_pct"], now, health["is_anomaly"]),
        )
        if health["status"] != "ONLINE":
            db.execute(
                """
                INSERT INTO downtime_logs (camera_id, camera_name, root_cause, failure_time, recovery_time, duration_minutes)
                VALUES (?, ?, ?, ?, NULL, NULL)
                """,
                (camera_id, body["name"], _root_cause(health["status"]), now),
            )
        row = db.execute("SELECT * FROM cameras WHERE id = ?", (camera_id,)).fetchone()
    log_activity("CAMERA_CREATED", f"Camera {body['name']} was registered and checked.")
    return row_to_dict(row)


def update_camera(camera_id, body):
    current = get_camera(camera_id)
    if not current:
        raise ValueError("Camera not found")
    fields = {
        "name": body.get("name", current["name"]),
        "location": body.get("location", current["location"]),
        "ip_address": body.get("ip_address", current["ip_address"]),
        "switch_id": body.get("switch_id", current["switch_id"]),
        "switch_ip": body.get("switch_ip", current.get("switch_ip", "")),
        "rtsp_url": body.get("rtsp_url", current["rtsp_url"]),
        "probe_mode": normalize_probe_mode(body.get("probe_mode"), current.get("probe_mode") or ""),
    }
    now = datetime.now().isoformat(timespec="seconds")
    health = check_camera_health({
        "id": camera_id,
        "ip_address": fields["ip_address"],
        "rtsp_url": fields["rtsp_url"],
        "probe_mode": fields["probe_mode"],
        "status": current.get("status"),
    })
    with connect() as db:
        db.execute(
            """
            UPDATE cameras
            SET name = ?, location = ?, ip_address = ?, switch_id = ?, switch_ip = ?, rtsp_url = ?, probe_mode = ?,
                status = ?, last_checked = ?, latency_ms = ?, stream_status = ?, stream_response_ms = ?, last_stream_check = ?
            WHERE id = ?
            """,
            (
                fields["name"], fields["location"], fields["ip_address"], fields["switch_id"], fields["switch_ip"],
                fields["rtsp_url"], fields["probe_mode"], health["status"], now, health["latency_ms"], health["stream_status"],
                health["stream_response_ms"], now, camera_id,
            ),
        )
        db.execute(
            """
            INSERT INTO ping_history (camera_id, response_time_ms, packet_loss_pct, recorded_at, is_anomaly)
            VALUES (?, ?, ?, ?, ?)
            """,
            (camera_id, health["latency_ms"], health["packet_loss_pct"], now, health["is_anomaly"]),
        )
        if health["status"] != current["status"] and health["status"] != "ONLINE":
            db.execute(
                """
                INSERT INTO downtime_logs (camera_id, camera_name, root_cause, failure_time, recovery_time, duration_minutes)
                VALUES (?, ?, ?, ?, NULL, NULL)
                """,
                (camera_id, fields["name"], _root_cause(health["status"]), now),
            )
    log_activity("CAMERA_UPDATED", f"Camera {fields['name']} was updated and checked.")
    return get_camera(camera_id)


def _root_cause(status):
    return {
        "OFFLINE": "POWER_OR_CABLE",
        "UNSTABLE": "UNSTABLE_CONNECTION_ML",
        "STREAM_FAILURE": "RTSP_STREAM_FAILURE",
    }.get(status, "CAMERA_HEALTH_CHANGE")


def delete_camera(camera_id):
    with connect() as db:
        db.execute("DELETE FROM ping_history WHERE camera_id = ?", (camera_id,))
        db.execute("DELETE FROM downtime_logs WHERE camera_id = ?", (camera_id,))
        db.execute("DELETE FROM alerts WHERE camera_id = ?", (camera_id,))
        db.execute("DELETE FROM cameras WHERE id = ?", (camera_id,))
    log_activity("CAMERA_DELETED", f"Camera id {camera_id} and related records were deleted.")


def get_alerts():
    with connect() as db:
        rows = db.execute("SELECT * FROM alerts ORDER BY sent_at DESC").fetchall()
        alerts = [row_to_dict(row) for row in rows]
        for alert in alerts:
            diag = db.execute(
                """
                SELECT severity, diagnosis, confidence, recommended_solution, resolution_status, created_at
                FROM diagnosis_history
                WHERE camera_id = ? OR camera_name = ?
                ORDER BY created_at DESC LIMIT 1
                """,
                (alert.get("camera_id"), alert.get("camera_name")),
            ).fetchone()
            if diag:
                alert.update({
                    "severity": diag["severity"],
                    "diagnosis": diag["diagnosis"],
                    "confidence": diag["confidence"],
                    "recommended_action": diag["recommended_solution"],
                    "resolution_status": diag["resolution_status"],
                })
            else:
                alert.update({
                    "severity": "INFO",
                    "diagnosis": "Operational Notification",
                    "confidence": None,
                    "recommended_action": "Review the camera health dashboard and acknowledge the alert after operational validation.",
                    "resolution_status": "OPEN" if not alert.get("is_read") else "ACKNOWLEDGED",
                })
        return alerts


def create_alert(camera_id, alert_type, message, is_read=0):
    camera = get_camera(camera_id)
    if not camera:
        raise ValueError("Camera not found")
    if alert_type not in ("EMAIL", "TELEGRAM"):
        raise ValueError("Only EMAIL and TELEGRAM alerts are supported")
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO alerts (camera_id, camera_name, alert_type, message, sent_at, is_read)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (camera_id, camera["name"], alert_type, message, datetime.now().isoformat(timespec="seconds"), is_read),
        )
        alert_id = cursor.lastrowid
    dispatch("ALERT_CREATED", {"alert_id": alert_id, "camera_id": camera_id, "name": camera["name"], "alert_type": alert_type})
    return alert_id


def create_system_alert(alert_type, title, message, is_read=0):
    if alert_type not in ("EMAIL", "TELEGRAM"):
        raise ValueError("Only EMAIL and TELEGRAM alerts are supported")
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO alerts (camera_id, camera_name, alert_type, message, sent_at, is_read)
            VALUES (NULL, ?, ?, ?, ?, ?)
            """,
            (title, alert_type, message, datetime.now().isoformat(timespec="seconds"), is_read),
        )
        alert_id = cursor.lastrowid
    dispatch("ALERT_CREATED", {"alert_id": alert_id, "name": title, "alert_type": alert_type})
    return alert_id


def unresolved_cameras_today():
    today = datetime.now().date().isoformat()
    with connect() as db:
        rows = db.execute(
            """
            SELECT * FROM cameras
            WHERE status != 'ONLINE'
            ORDER BY switch_id, location, name
            """
        ).fetchall()
    return [d for d in (row_to_dict(row) for row in rows) if (d.get("last_checked") or "")[:10] <= today]


def build_daily_email_body(cameras):
    report_date = datetime.now().strftime("%d %B %Y")
    lines = [
        "UCEK-JNTUK Camera Health Monitoring System",
        f"Daily Unresolved Camera Downtime Report - {report_date}",
        "",
        "This report lists cameras that are currently not in recovered/online condition as of the report generation time.",
        "",
    ]
    if not cameras:
        lines.append("No unresolved camera outages are currently recorded for UCEK-JNTUK.")
    else:
        for index, camera in enumerate(cameras, start=1):
            lines.extend([
                f"{index}. {camera['name']}",
                f"   Location        : {camera['location']}",
                f"   Camera IP       : {camera['ip_address']}",
                f"   Switch          : {camera['switch_id']} ({camera.get('switch_ip') or 'switch IP not available'})",
                f"   Status          : {camera['status']}",
                f"   Stream Health   : {camera['stream_status']}",
                f"   Ping Latency    : {camera['latency_ms'] if camera['latency_ms'] is not None else 'No response'} ms",
                f"   Stream Response : {camera.get('stream_response_ms') if camera.get('stream_response_ms') is not None else 'Unavailable'} ms",
                f"   Last Check      : {camera['last_checked']}",
                "",
            ])
    lines.extend([
        "Recommended action:",
        "Please assign the pending items to the network/campus surveillance maintenance team and update recovery status after physical verification.",
        "",
        "Regards,",
        "UCEK-JNTUK Camera Health Monitoring System",
    ])
    return "\n".join(lines)


def send_daily_email_report_if_due():
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat(timespec="seconds")
    with connect() as db:
        recent = db.execute(
            """
            SELECT id FROM alerts
            WHERE alert_type = 'EMAIL'
              AND camera_name = 'UCEK-JNTUK Daily Report'
              AND sent_at >= ?
            ORDER BY sent_at DESC LIMIT 1
            """,
            (cutoff,),
        ).fetchone()
    if recent:
        return {"ok": True, "skipped": True, "reason": "Daily email report was already generated within the last 24 hours"}
    down_cameras = unresolved_cameras_today()
    subject = f"UCEK-JNTUK Daily Camera Downtime Report - {datetime.now().strftime('%d %b %Y')}"
    body = build_daily_email_body(down_cameras)
    delivery = send_email_report(subject, body)
    alert_id = create_system_alert("EMAIL", "UCEK-JNTUK Daily Report", body[:900])
    record_notification("EMAIL", "Configured email recipients", delivery, None, None)
    log_activity("DAILY_EMAIL_REPORT", f"Daily email report generated with {len(down_cameras)} unresolved camera item(s).")
    return {"ok": True, "alert_id": alert_id, "delivery": delivery, "cameras_reported": len(down_cameras), "skipped": False}


def build_telegram_network_message():
    cameras = get_cameras()
    by_switch = {}
    for camera in cameras:
        by_switch.setdefault(camera["switch_id"], []).append(camera)
    lines = ["UCEK-JNTUK Camera Health Monitoring - Network Alert", datetime.now().strftime("%d %b %Y, %I:%M %p"), ""]
    reported = 0
    for switch_id, switch_cameras in sorted(by_switch.items()):
        offline = [camera for camera in switch_cameras if camera["status"] == "OFFLINE"]
        unhealthy = [camera for camera in switch_cameras if camera["status"] != "ONLINE"]
        if len(offline) == len(switch_cameras) and len(switch_cameras) > 1:
            switch_ip = switch_cameras[0].get("switch_ip") or "switch IP not available"
            lines.append(f"SWITCH DOWN: {switch_id} ({switch_ip})")
            lines.append(f"Affected cameras: {len(switch_cameras)}")
            lines.append("Action: Verify switch power, uplink and network rack connectivity.")
            lines.append("")
            reported += 1
        else:
            for camera in unhealthy:
                lines.append(f"CAMERA {camera['status']}: {camera['name']}")
                lines.append(f"Location: {camera['location']} | IP: {camera['ip_address']} | Switch: {camera['switch_id']}")
                lines.append(f"Health: {camera['stream_status']}")
                lines.append("")
                reported += 1
    if reported == 0:
        lines.append("All registered cameras are currently online.")
    return "\n".join(lines), reported


def send_telegram_network_alert():
    message, reported = build_telegram_network_message()
    delivery = send_telegram_message(message)
    alert_id = create_system_alert("TELEGRAM", "UCEK-JNTUK Network Alert", message[:900])
    record_notification("TELEGRAM", "Configured Telegram Chat", delivery, None, None)
    log_activity("TELEGRAM_NETWORK_ALERT", f"Telegram network alert generated with {reported} item(s).")
    return {"ok": True, "alert_id": alert_id, "delivery": delivery, "items_reported": reported}


def mark_alert_read(alert_id):
    with connect() as db:
        db.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert_id,))


def update_camera_status(camera_id, status):
    if status not in ("ONLINE", "OFFLINE", "UNSTABLE", "STREAM_FAILURE"):
        raise ValueError("Invalid status")
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as db:
        db.execute("UPDATE cameras SET status = ?, last_checked = ? WHERE id = ?", (status, now, camera_id))
    camera = get_camera(camera_id)
    dispatch("STREAM_FAILURE" if status == "STREAM_FAILURE" else ("CAMERA_OFFLINE" if status == "OFFLINE" else "CAMERA_ONLINE"), camera)


def monitor_tick():
    return SCHEDULER.trigger()


def start_monitor_once():
    global MONITOR_STARTED
    if MONITOR_STARTED:
        return
    MONITOR_STARTED = True
    SCHEDULER.start()


def start_websocket_once():
    global WEBSOCKET_STARTED
    if WEBSOCKET_STARTED:
        return
    WEBSOCKET_STARTED = True
    start_websocket_server("127.0.0.1", 8001)


def start_alert_scheduler_once():
    global ALERT_SCHEDULER_STARTED
    if ALERT_SCHEDULER_STARTED:
        return
    ALERT_SCHEDULER_STARTED = True
    ALERT_SCHEDULER.start()


def start_model_scheduler_once():
    global MODEL_SCHEDULER_STARTED
    if MODEL_SCHEDULER_STARTED:
        return
    MODEL_SCHEDULER_STARTED = True
    MODEL_SCHEDULER.start()






def record_diagnosis(camera, health=None, source_event="MANUAL_REVIEW", resolution_status="OPEN"):
    diagnosis = diagnose_camera(camera, health)
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO diagnosis_history
            (camera_id, camera_name, severity, diagnosis, confidence, recommended_solution, source_event, resolution_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                camera.get("id"), camera.get("name", "Unknown Camera"), diagnosis["severity"],
                diagnosis["diagnosis"], diagnosis["confidence"], diagnosis["recommended_solution"],
                source_event, resolution_status, now,
            ),
        )
    diagnosis["id"] = cursor.lastrowid
    diagnosis["camera_id"] = camera.get("id")
    diagnosis["camera_name"] = camera.get("name", "Unknown Camera")
    diagnosis["timestamp"] = now
    diagnosis["resolution_status"] = resolution_status
    return diagnosis


def record_notification(notification_type, recipient, delivery, camera=None, diagnosis=None, status=None):
    now = datetime.now().isoformat(timespec="seconds")
    delivery_result = delivery.get("reason") or delivery.get("channel") or "Notification event recorded"
    notification_status = status or ("DELIVERED" if delivery.get("sent") else "SKIPPED")
    with connect() as db:
        db.execute(
            """
            INSERT INTO notification_history
            (notification_type, recipient, status, delivery_result, camera_id, camera_name, severity, diagnosis, confidence, recommended_action, resolution_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                notification_type, recipient, notification_status, delivery_result,
                camera.get("id") if camera else None,
                camera.get("name") if camera else None,
                diagnosis.get("severity") if diagnosis else None,
                diagnosis.get("diagnosis") if diagnosis else None,
                diagnosis.get("confidence") if diagnosis else None,
                diagnosis.get("recommended_solution") if diagnosis else None,
                diagnosis.get("resolution_status", "OPEN") if diagnosis else "OPEN",
                now,
            ),
        )
    log_activity(f"{notification_type}_EVENT", f"{notification_type} notification {notification_status.lower()}: {delivery_result}")


def get_diagnosis_history():
    with connect() as db:
        rows = db.execute("SELECT * FROM diagnosis_history ORDER BY created_at DESC LIMIT 300").fetchall()
        return [row_to_dict(row) for row in rows]


def get_diagnosis_summary():
    rows = get_diagnosis_history()
    counts = {}
    open_items = 0
    for row in rows:
        counts[row["diagnosis"]] = counts.get(row["diagnosis"], 0) + 1
        if row.get("resolution_status") == "OPEN":
            open_items += 1
    return {"total": len(rows), "open": open_items, "by_diagnosis": counts}


def get_recommendations():
    return {key: recommendation_text(key) for key in RECOMMENDATIONS}


def get_platform_status():
    stats = get_stats()
    runtime = monitor_runtime()
    monitoring = "Active" if runtime.get("alive") else ("Starting" if runtime.get("started") and not runtime.get("last_success_at") else "Degraded")
    return {
        "platform_status": "Monitoring Active" if runtime.get("alive") else "Monitoring Attention Required",
        "camera_monitoring": monitoring,
        "notification_service": "Configured" if (email_configured() or telegram_configured()) else "Pending Configuration",
        "last_synchronization": runtime.get("last_success_at"),
        "last_monitor_tick": runtime.get("last_success_at"),
        "monitor_error": runtime.get("last_error"),
        "demo_mode": DEMO_MODE,
        "system_health": "Healthy" if stats["offline"] == 0 and stats["unstable"] == 0 and stats.get("stream_failure", 0) == 0 else "Attention Required",
    }


def get_monitoring_status():
    stats = get_stats()
    runtime = monitor_runtime()
    return {
        "camera_monitoring": "Active" if runtime.get("alive") else "Degraded",
        "total_cameras": stats["total"],
        "healthy_cameras": stats["online"],
        "warning_cameras": stats["unstable"] + stats.get("stream_failure", 0),
        "offline_cameras": stats["offline"],
        "switches": stats.get("switches", {}),
        "last_synchronization": runtime.get("last_success_at"),
        "last_monitor_tick": runtime.get("last_success_at"),
        "monitor_error": runtime.get("last_error"),
    }


def get_public_health():
    runtime = monitor_runtime()
    return {
        "ok": True,
        "database": "sqlite",
        "sms_enabled": False,
        "websocket_port": 8001,
        "demo_mode": DEMO_MODE,
        "monitor": runtime,
    }


def get_notification_history():
    with connect() as db:
        rows = db.execute("SELECT * FROM notification_history ORDER BY created_at DESC LIMIT 300").fetchall()
        history = [row_to_dict(row) for row in rows]
    if history:
        return history
    alerts = get_alerts()
    fallback = []
    for alert in alerts:
        fallback.append({
            "id": alert["id"],
            "notification_type": alert["alert_type"],
            "recipient": "Configured recipients",
            "status": "Delivered" if alert.get("is_read") else "Sent",
            "delivery_result": alert["message"],
            "created_at": alert["sent_at"],
            "camera_id": alert.get("camera_id"),
            "camera_name": alert.get("camera_name"),
            "resolution_status": "OPEN" if not alert.get("is_read") else "ACKNOWLEDGED",
        })
    return fallback


def get_ml_statistics():
    rows = latest_predictions()
    high = [row for row in rows if row.get("risk_level") in ("HIGH", "CRITICAL")]
    last_time = max([row.get("created_at") for row in rows if row.get("created_at")] or [None])
    covered = len({row.get("camera_id") for row in rows if row.get("camera_id")})
    total = len(get_cameras())
    return {
        "model_status": "Active" if rows else "Awaiting Analysis",
        "prediction_accuracy": None,
        "prediction_coverage": round((covered / total * 100), 1) if total else 0,
        "last_analysis": last_time,
        "prediction_count": len(rows),
        "high_risk_camera_count": len(high),
    }


def get_dashboard_summary():
    stats = get_stats()
    health_pct = round((stats["online"] / stats["total"] * 100), 1) if stats["total"] else 0
    return {
        "statistics": stats,
        "health_score": health_pct,
        "platform_status": get_platform_status(),
        "ml_statistics": get_ml_statistics(),
        "diagnosis_summary": get_diagnosis_summary(),
        "incident_summary": get_incident_summary(),
        "maintenance_summary": MaintenanceService().summary(),
        "last_synchronization": datetime.now().isoformat(timespec="seconds"),
    }
def get_logs():
    with connect() as db:
        rows = db.execute("SELECT * FROM downtime_logs ORDER BY failure_time DESC").fetchall()
        return [row_to_dict(row) for row in rows]


def get_ping_history(camera_id):
    with connect() as db:
        rows = db.execute("SELECT * FROM ping_history WHERE camera_id = ? ORDER BY recorded_at DESC LIMIT 200", (camera_id,)).fetchall()
        return [row_to_dict(row) for row in rows]

def get_prediction_history(camera_id):
    with connect() as db:
        rows = db.execute(
            """
            SELECT p.*, c.name AS camera_name
            FROM predictions p
            JOIN cameras c ON c.id = p.camera_id
            WHERE p.camera_id = ?
            ORDER BY p.created_at DESC
            LIMIT 50
            """,
            (camera_id,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def get_escalations():
    cutoff = (datetime.now() - timedelta(days=7)).isoformat(timespec="seconds")
    with connect() as db:
        rows = db.execute(
            """
            SELECT * FROM escalations
            WHERE status = 'ACTIVE' OR triggered_at >= ?
            ORDER BY triggered_at DESC
            """,
            (cutoff,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]



def user_public(row):
    data = row_to_dict(row)
    data.pop("password_hash", None)
    return data


def login_user(body):
    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not row or not row["is_active"] or not verify_password(password, row["password_hash"]):
            return None
        now = datetime.now().isoformat(timespec="seconds")
        db.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, row["id"]))
        refreshed = db.execute("SELECT * FROM users WHERE id = ?", (row["id"],)).fetchone()
    user = user_public(refreshed)
    token = create_token(user["id"], user["username"], user["role"])
    return {"ok": True, "token": token, "user": {"id": user["id"], "username": user["username"], "full_name": user["full_name"], "role": user["role"], "email": user["email"]}}


def get_current_user(payload):
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (payload["user_id"],)).fetchone()
        return user_public(row) if row else None


def list_users():
    with connect() as db:
        rows = db.execute("SELECT * FROM users ORDER BY id").fetchall()
        return [user_public(row) for row in rows]


def create_user(body):
    required = ["username", "full_name", "email", "password", "role"]
    missing = [field for field in required if not body.get(field)]
    if missing:
        raise ValueError("Missing fields: " + ", ".join(missing))
    if body["role"] not in ("ADMINISTRATOR", "NETWORK_ENGINEER", "OPERATOR", "VIEWER"):
        raise ValueError("Invalid role")
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO users (username, full_name, email, password_hash, role, is_active, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, 1, ?, NULL)
            """,
            (body["username"], body["full_name"], body["email"], hash_password(body["password"]), body["role"], now),
        )
        row = db.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return user_public(row)


def update_user_password(user_id, body):
    new_password = body.get("new_password") or ""
    if len(new_password) < 8:
        raise ValueError("Password must be at least 8 characters")
    with connect() as db:
        db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_password), user_id))


def backup_loop():
    while True:
        try:
            backup_database()
        except Exception:
            logging.exception("Database backup failed")
        time.sleep(86400)


def start_backup_once():
    threading.Thread(target=backup_loop, daemon=True).start()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_OPTIONS(self):
        self.send_response(204)
        _apply_cors_headers(self)
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            user = api_user(self, path, "GET")
            if path.startswith("/api/") and user is None:
                return
            if path in ("/api/reports/daily", "/api/reports/weekly", "/api/reports/monthly"):
                if not user or user.get("role") not in ("ADMINISTRATOR", "NETWORK_ENGINEER", "OPERATOR"):
                    json_response(self, {"error": "Permission denied"}, 403)
                    return
                report_response(self, path, parsed.query)
            elif path == "/api/health":
                json_response(self, get_public_health())
            elif path == "/api/config/status":
                json_response(self, {"email_configured": email_configured(), "telegram_configured": telegram_configured(), "sms_enabled": False})
            elif path == "/api/auth/me":
                current = get_current_user(user)
                json_response(self, {"ok": True, "user": current} if current else {"error": "User not found"}, 200 if current else 404)
            elif path == "/api/users":
                if user.get("role") != "ADMINISTRATOR":
                    json_response(self, {"error": "Permission denied"}, 403)
                    return
                json_response(self, list_users())
            elif path == "/api/cameras":
                json_response(self, sanitize_cameras(get_cameras(), user))
            elif path == "/api/cameras/stats":
                json_response(self, get_stats())
            elif path == "/api/cameras/health-summary":
                cameras = get_cameras()
                total = len(cameras)
                healthy = sum(1 for c in cameras if c["status"] == "ONLINE")
                warning = sum(1 for c in cameras if c["status"] == "UNSTABLE")
                offline = sum(1 for c in cameras if c["status"] == "OFFLINE")
                stream_fail = sum(1 for c in cameras if c["status"] == "STREAM_FAILURE")
                health_pct = round((healthy / total * 100), 1) if total else 0
                json_response(self, {
                    "total": total,
                    "healthy": healthy,
                    "warning": warning,
                    "offline": offline,
                    "stream_failure": stream_fail,
                    "health_percentage": health_pct,
                    "status": "healthy" if health_pct >= 80 else "warning" if health_pct >= 50 else "critical"
                })
            elif path == "/api/cameras/latency-stats":
                cameras = get_cameras()
                latencies = [c["latency_ms"] for c in cameras if c.get("latency_ms") is not None]
                avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else None
                max_latency = max(latencies) if latencies else None
                min_latency = min(latencies) if latencies else None
                json_response(self, {
                    "avg_latency_ms": avg_latency,
                    "max_latency_ms": max_latency,
                    "min_latency_ms": min_latency,
                    "cameras_with_data": len(latencies),
                    "cameras_no_response": len(cameras) - len(latencies)
                })
            elif path == "/api/platform/status":
                json_response(self, get_platform_status())
            elif path == "/api/monitoring/status":
                json_response(self, get_monitoring_status())
            elif path == "/api/notifications/history":
                json_response(self, get_notification_history())
            elif path == "/api/ml/statistics":
                json_response(self, get_ml_statistics())
            elif path == "/api/diagnosis/history":
                json_response(self, get_diagnosis_history())
            elif path == "/api/recommendations":
                json_response(self, get_recommendations())
            elif path == "/api/dashboard/summary":
                json_response(self, get_dashboard_summary())
            elif path == "/api/topology":
                json_response(self, get_topology_data())
            elif path == "/api/analytics/summary":
                json_response(self, get_camera_analytics())
            elif path == "/api/analytics/downtime-trend":
                json_response(self, get_downtime_trend())
            elif path == "/api/analytics/system":
                json_response(self, get_system_summary())
            elif path == "/api/predictions":
                json_response(self, latest_predictions())
            elif path == "/api/cameras/stream-status":
                json_response(self, get_stream_status())
            elif path.startswith("/api/predictions/"):
                try:
                    target_id = int(path.split("/")[-1])
                except (ValueError, IndexError):
                    json_response(self, {"error": "Invalid camera ID"}, 400)
                    return
                json_response(self, get_prediction_history(target_id))
            elif path == "/api/escalations":
                json_response(self, get_escalations())
            elif path == "/api/switches/stats":
                json_response(self, switch_stats())
            elif path == "/api/switches":
                json_response(self, [sanitize_switch(item, user) for item in SwitchService().list_switches()])
            elif path.startswith("/api/switches/"):
                switch_id = path.split("/")[-1]
                switch = SwitchService().get_switch(switch_id)
                json_response(self, sanitize_switch(switch, user) if switch else {"error": "Switch not found"}, 200 if switch else 404)
            elif path == "/api/settings":
                json_response(self, get_settings())
            elif path == "/api/user-activity":
                json_response(self, get_user_activity())
            elif path == "/api/maintenance/summary":
                json_response(self, MaintenanceService().summary())
            elif path == "/api/maintenance/sessions":
                query = parse_qs(parsed.query)
                status = (query.get("status") or [None])[0]
                json_response(self, MaintenanceService().list_sessions(status))
            elif path == "/api/root-cause/analytics":
                query = parse_qs(parsed.query)
                filters = {key: values[0] for key, values in query.items() if values}
                json_response(self, RootCauseAnalyticsService().summary(filters))
            elif path == "/api/ai-performance":
                json_response(self, AIFeedbackService().performance())
            elif path == "/api/ai-feedback":
                json_response(self, AIFeedbackService().list_feedback())
            elif path == "/api/enterprise-reports/daily":
                json_response(self, ReportService().list_reports("daily"))
            elif path == "/api/enterprise-reports/monthly":
                json_response(self, ReportService().list_reports("monthly"))
            elif path.startswith("/api/enterprise-reports/daily/"):
                try:
                    report_id = int(path.split("/")[-1])
                except (ValueError, IndexError):
                    json_response(self, {"error": "Invalid report ID"}, 400)
                    return
                report = ReportService().get_report("daily", report_id)
                json_response(self, report if report else {"error": "Report not found"}, 200 if report else 404)
            elif path.startswith("/api/enterprise-reports/monthly/"):
                try:
                    report_id = int(path.split("/")[-1])
                except (ValueError, IndexError):
                    json_response(self, {"error": "Invalid report ID"}, 400)
                    return
                report = ReportService().get_report("monthly", report_id)
                json_response(self, report if report else {"error": "Report not found"}, 200 if report else 404)
            elif path.startswith("/api/cameras/") and path.endswith("/ping-history"):
                try:
                    camera_id = int(path.split("/")[3])
                except (ValueError, IndexError):
                    json_response(self, {"error": "Invalid camera ID"}, 400)
                    return
                json_response(self, get_ping_history(camera_id))
            elif path.startswith("/api/cameras/"):
                try:
                    camera_id = int(path.split("/")[-1])
                except (ValueError, IndexError):
                    json_response(self, {"error": "Invalid camera ID"}, 400)
                    return
                camera = get_camera(camera_id)
                json_response(self, sanitize_camera(camera, user) if camera else {"error": "Camera not found"}, 200 if camera else 404)
            elif path == "/api/alerts":
                json_response(self, get_alerts())
            elif path == "/api/logs":
                json_response(self, get_logs())
            elif path.startswith("/api/"):
                json_response(self, {"error": "Not found"}, 404)
            else:
                self.serve_static(path)
        except ValueError as exc:
            json_response(self, {"error": str(exc)}, 400)
        except Exception as exc:
            logging.exception("Unhandled error in do_GET: %s", exc)
            json_response(self, {"error": "Internal server error"}, 500)
    def do_POST(self):
        path = urlparse(self.path).path
        try:
            user = api_user(self, path, "POST")
            if path.startswith("/api/") and user is None:
                return
            if path == "/api/auth/login":
                result = login_user(read_body(self))
                json_response(self, result if result else {"error": "Invalid credentials"}, 200 if result else 401)
            elif path == "/api/auth/logout":
                json_response(self, {"ok": True, "message": "Logged out successfully"})
            elif path == "/api/users":
                if not require_auth(self, ["ADMINISTRATOR"]):
                    return
                json_response(self, {"ok": True, "user": create_user(read_body(self))}, 201)
            elif path == "/api/monitor/tick":
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                json_response(self, monitor_tick())
            elif path == "/api/predictions/run":
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                json_response(self, {"ok": True, "predictions": run_all_predictions()})
            elif path == "/api/cameras":
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                json_response(self, {"ok": True, "camera": sanitize_camera(create_camera(read_body(self)), user)}, 201)
            elif path.startswith("/api/cameras/") and path.endswith("/maintenance/start"):
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                camera_id = int(path.split("/")[3])
                body = read_body(self)
                session = MaintenanceService().start(camera_id, body.get("maintenance_reason") or body.get("reason") or "Maintenance", body.get("technician_name") or "Technician", body.get("expected_end_time"), body.get("notes", ""))
                json_response(self, {"ok": True, "maintenance": session}, 201)
            elif path.startswith("/api/cameras/") and path.endswith("/maintenance/complete"):
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                camera_id = int(path.split("/")[3])
                body = read_body(self)
                session = MaintenanceService().complete(camera_id, body.get("notes", ""))
                json_response(self, {"ok": True, "maintenance": session})
            elif path == "/api/ai-feedback":
                if not user or user.get("public"):
                    json_response(self, {"error": "Authorization token required"}, 401)
                    return
                body = read_body(self)
                result = AIFeedbackService().submit(int(body.get("incident_id")), bool(body.get("diagnosis_correct")), body.get("operator") or "Dashboard operator", body.get("actual_cause"), body.get("resolution_notes", ""))
                json_response(self, result, 201)
            elif path.startswith("/api/switches/") and path.endswith("/maintenance/start"):
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                switch_id = path.split("/")[3]
                body = read_body(self)
                session = MaintenanceService().start_asset("SWITCH", switch_id, body.get("maintenance_reason") or body.get("reason") or "Maintenance", body.get("technician_name") or "Technician", body.get("expected_end_time"), body.get("notes", ""))
                json_response(self, {"ok": True, "maintenance": session}, 201)
            elif path.startswith("/api/switches/") and path.endswith("/maintenance/complete"):
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                switch_id = path.split("/")[3]
                body = read_body(self)
                session = MaintenanceService().complete_asset("SWITCH", switch_id, body.get("notes", ""), body.get("version"))
                json_response(self, {"ok": True, "maintenance": session})
            elif path == "/api/root-cause/analytics/refresh":
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                json_response(self, RootCauseAnalyticsService().refresh_statistics())
            elif path == "/api/enterprise-reports/daily/generate":
                if not require_auth(self, ["ADMINISTRATOR"]):
                    return
                body = read_body(self)
                json_response(self, ReportService().generate_daily(send_email=bool(body.get("send_email"))))
            elif path == "/api/enterprise-reports/monthly/generate":
                if not require_auth(self, ["ADMINISTRATOR"]):
                    return
                json_response(self, ReportService().generate_monthly())
            elif path in ("/api/alerts/daily-email-report", "/api/alerts/telegram-network-alert"):
                json_response(self, {"error": "Manual notification triggers are disabled. Email and Telegram delivery are automatic."}, 404)
            else:
                json_response(self, {"error": "Not found"}, 404)
        except Exception as exc:
            json_response(self, {"error": str(exc)}, 400)

    def do_PUT(self):
        path = urlparse(self.path).path
        try:
            user = api_user(self, path, "PUT")
            if path.startswith("/api/") and user is None:
                return
            if path == "/api/settings":
                if not require_auth(self, ["ADMINISTRATOR"]):
                    return
                json_response(self, {"ok": True, "settings": update_settings(read_body(self))})
            elif path.startswith("/api/users/") and path.endswith("/password"):
                if not require_auth(self, ["ADMINISTRATOR"]):
                    return
                update_user_password(int(path.split("/")[3]), read_body(self))
                json_response(self, {"ok": True})
            elif path.startswith("/api/alerts/") and path.endswith("/read"):
                mark_alert_read(int(path.split("/")[3]))
                json_response(self, {"ok": True})
            elif path.startswith("/api/incidents/") and path.endswith("/acknowledge"):
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER", "OPERATOR"]):
                    return
                body = read_body(self)
                try:
                    incident_id = int(path.split("/")[3])
                except (ValueError, IndexError):
                    json_response(self, {"error": "Invalid incident ID"}, 400)
                    return
                operator = body.get("acknowledged_by") or (user.get("username") if user else "Dashboard operator")
                with connect() as db:
                    incident = IncidentService().repo.acknowledge(db, incident_id, operator, datetime.now().isoformat(timespec="seconds"))
                json_response(self, {"ok": bool(incident), "incident": incident} if incident else {"error": "Incident not found"}, 200 if incident else 404)
            elif path.startswith("/api/maintenance/sessions/"):
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                session_id = int(path.split("/")[-1])
                session = MaintenanceService().update_session(session_id, read_body(self))
                json_response(self, {"ok": True, "maintenance": session})
            elif path.startswith("/api/cameras/") and path.endswith("/status"):
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                camera_id = int(path.split("/")[3])
                body = read_body(self)
                update_camera_status(camera_id, body.get("status"))
                json_response(self, {"ok": True, "camera": sanitize_camera(get_camera(camera_id), user)})
            elif path.startswith("/api/cameras/"):
                if not require_auth(self, ["ADMINISTRATOR", "NETWORK_ENGINEER"]):
                    return
                camera_id = int(path.split("/")[-1])
                json_response(self, {"ok": True, "camera": sanitize_camera(update_camera(camera_id, read_body(self)), user)})
            else:
                json_response(self, {"error": "Not found"}, 404)
        except Exception as exc:
            json_response(self, {"error": str(exc)}, 400)

    def do_DELETE(self):
        path = urlparse(self.path).path
        try:
            user = api_user(self, path, "DELETE")
            if path.startswith("/api/") and user is None:
                return
            if path.startswith("/api/cameras/"):
                if not require_auth(self, ["ADMINISTRATOR"]):
                    return
                delete_camera(int(path.split("/")[-1]))
                json_response(self, {"ok": True})
            else:
                json_response(self, {"error": "Not found"}, 404)
        except Exception as exc:
            json_response(self, {"error": str(exc)}, 400)

    def serve_static(self, path):
        dist = DIST_DIR.resolve()
        if path in ("", "/"):
            candidate = dist / "index.html"
        else:
            candidate = (dist / path.lstrip("/")).resolve()
        try:
            candidate.relative_to(dist)
        except ValueError:
            self.send_error(403, "Forbidden")
            return
        if not candidate.is_file():
            candidate = (dist / "index.html").resolve()
            try:
                candidate.relative_to(dist)
            except ValueError:
                self.send_error(403, "Forbidden")
                return
        if candidate.suffix.lower() in BLOCKED_STATIC_SUFFIXES:
            self.send_error(403, "Forbidden")
            return
        body = candidate.read_bytes()
        mime_map = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".ico": "image/x-icon",
            ".woff2": "font/woff2",
            ".woff": "font/woff",
        }
        content_type = mime_map.get(candidate.suffix.lower(), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.end_headers()
        self.wfile.write(body)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    validate_runtime_secrets()
    init_db()
    IncidentService().synchronize_current_failures()
    ensure_models()
    start_websocket_once()
    start_monitor_once()
    start_alert_scheduler_once()
    start_model_scheduler_once()
    start_backup_once()
    print(f"Backend running at http://{HOST}:{PORT}")
    print("WebSocket running at ws://127.0.0.1:8001")
    print(f"Dashboard: http://{HOST}:{PORT}/")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()















