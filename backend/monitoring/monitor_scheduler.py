"""Scheduler that runs ping and RTSP checks and publishes health changes."""

import random
import threading
import time
from datetime import datetime

from database import connect, row_to_dict
from diagnosis_engine import diagnose_camera
from incidents import IncidentService
from monitoring.health_classifier import classify_health
from monitoring.ping_monitor import run_ping
from monitoring.rtsp_monitor import check_rtsp
from websocket.event_dispatcher import dispatch



def _send_automatic_telegram(message):
    try:
        import sys
        from pathlib import Path
        backend_dir = Path(__file__).resolve().parents[1]
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        from alerts import send_telegram_message
        return send_telegram_message(message)
    except Exception as exc:
        return {"sent": False, "reason": str(exc)}


def _record_notification(db, notification_type, camera, diagnosis, delivery, now):
    db.execute(
        """
        INSERT INTO notification_history
        (notification_type, recipient, status, delivery_result, camera_id, camera_name, severity, diagnosis, confidence, recommended_action, resolution_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            notification_type,
            "Configured Telegram Chat",
            "DELIVERED" if delivery.get("sent") else "SKIPPED",
            delivery.get("reason") or delivery.get("channel") or "Automatic notification event recorded",
            camera["id"],
            camera["name"],
            diagnosis["severity"],
            diagnosis["diagnosis"],
            diagnosis["confidence"],
            diagnosis["recommended_solution"],
            "OPEN",
            now,
        ),
    )
def _escalation_engine():
    try:
        import sys
        from pathlib import Path
        alerts_dir = Path(__file__).resolve().parents[1] / "alerts"
        if str(alerts_dir) not in sys.path:
            sys.path.insert(0, str(alerts_dir))
        from escalation_engine import EscalationEngine
        return EscalationEngine()
    except Exception:
        return None


class MonitorScheduler:
    """Run camera health checks manually or on a background interval."""

    def __init__(self, interval_seconds=30):
        self.interval_seconds = interval_seconds
        self._started = False
        self._lock = threading.Lock()

    def run_once(self):
        now = datetime.now().isoformat(timespec="seconds")
        with self._lock:
            with connect() as db:
                cameras = [row_to_dict(row) for row in db.execute("SELECT * FROM cameras ORDER BY id").fetchall()]
                for camera in cameras:
                    previous_status = camera.get("status")
                    health = self._check_camera(camera)
                    db.execute(
                        """
                        INSERT INTO ping_history (camera_id, response_time_ms, packet_loss_pct, recorded_at, is_anomaly)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (camera["id"], health["latency_ms"], health["packet_loss_pct"], now, health["is_anomaly"]),
                    )
                    db.execute(
                        """
                        UPDATE cameras
                        SET status = ?, last_checked = ?, latency_ms = ?, stream_status = ?,
                            stream_response_ms = ?, last_stream_check = ?
                        WHERE id = ?
                        """,
                        (
                            health["status"], now, health["latency_ms"], health["stream_status"],
                            health["stream_response_ms"], now, camera["id"],
                        ),
                    )
                    if health["status"] != previous_status:
                        self._record_status_change(db, camera, previous_status, health, now)
                        self._dispatch_status_change(camera, previous_status, health)
        return {"ok": True, "checked": len(cameras), "at": now}

    def _check_camera(self, camera):
        ip_address = camera.get("ip_address") or ""
        rtsp_url = camera.get("rtsp_url") or ""
        if ip_address.startswith("192.168.10."):
            ping_result = self._demo_ping(camera)
            rtsp_result = self._demo_rtsp(camera, rtsp_url, ping_result)
        else:
            ping_result = run_ping(ip_address)
            rtsp_result = check_rtsp(rtsp_url)
        return classify_health(ping_result, rtsp_result, rtsp_url)

    @staticmethod
    def _demo_ping(camera):
        if camera.get("status") == "OFFLINE" and random.random() < 0.7:
            return {"success": False, "latency_ms": None, "packet_loss_pct": 100}
        base = 18 + int(camera["id"]) * 4
        jitter = random.randint(0, 170 if int(camera["id"]) in (2, 6) else 35)
        latency = base + jitter
        return {"success": True, "latency_ms": latency, "packet_loss_pct": 10 if latency > 155 else 0}

    @staticmethod
    def _demo_rtsp(camera, rtsp_url, ping_result):
        if not rtsp_url:
            return {"success": False, "response_ms": None, "error": "No RTSP URL configured"}
        if not ping_result.get("success"):
            return {"success": False, "response_ms": None, "error": "Camera unreachable"}
        if int(camera["id"]) == 3 and random.random() < 0.35:
            return {"success": False, "response_ms": None, "error": "RTSP port unavailable"}
        return {"success": True, "response_ms": random.randint(24, 95), "error": None}

    @staticmethod
    def _record_status_change(db, camera, previous_status, health, now):
        if health["status"] == "ONLINE" and previous_status != "ONLINE":
            db.execute(
                """
                UPDATE downtime_logs
                SET recovery_time = ?, duration_minutes = CAST((julianday(?) - julianday(failure_time)) * 24 * 60 AS INTEGER)
                WHERE camera_id = ? AND recovery_time IS NULL
                """,
                (now, now, camera["id"]),
            )
            db.execute(
                "UPDATE diagnosis_history SET resolution_status = 'RESOLVED' WHERE camera_id = ? AND resolution_status = 'OPEN'",
                (camera["id"],),
            )
            IncidentService().resolve_camera(db, camera, now)
            return
        diagnosis = diagnose_camera(camera, health)
        db.execute(
            """
            INSERT INTO diagnosis_history
            (camera_id, camera_name, severity, diagnosis, confidence, recommended_solution, source_event, resolution_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?)
            """,
            (camera["id"], camera["name"], diagnosis["severity"], diagnosis["diagnosis"], diagnosis["confidence"], diagnosis["recommended_solution"], health["status"], now),
        )
        db.execute(
            """
            INSERT INTO downtime_logs (camera_id, camera_name, root_cause, failure_time, recovery_time, duration_minutes)
            VALUES (?, ?, ?, ?, NULL, NULL)
            """,
            (camera["id"], camera["name"], diagnosis["diagnosis"].upper().replace(" ", "_"), now),
        )
        if health["status"] in ("OFFLINE", "STREAM_FAILURE", "UNSTABLE"):
            IncidentService().handle_camera_failure(db, camera, health, diagnosis, now)

    @staticmethod
    def _dispatch_status_change(camera, previous_status, health):
        payload = {
            "camera_id": camera["id"],
            "name": camera["name"],
            "status": health["status"],
            "previous_status": previous_status,
            "stream_status": health["stream_status"],
            "latency_ms": health["latency_ms"],
            "stream_response_ms": health["stream_response_ms"],
        }
        if health["status"] == "STREAM_FAILURE":
            dispatch("STREAM_FAILURE", payload)
        elif health["status"] == "OFFLINE":
            dispatch("CAMERA_OFFLINE", payload)
        elif health["status"] == "ONLINE" and previous_status == "STREAM_FAILURE":
            dispatch("STREAM_RECOVERED", payload)
        elif health["status"] == "ONLINE":
            dispatch("CAMERA_ONLINE", payload)

    def start(self):
        if self._started:
            return
        self._started = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            try:
                self.run_once()
            except Exception:
                pass
            time.sleep(self.interval_seconds)

    def trigger(self):
        return self.run_once()








