"""Scheduler that runs ping and RTSP-port checks and publishes health changes."""

import logging
import threading
import time
from datetime import datetime

from database import connect, row_to_dict
from diagnosis_engine import diagnose_camera
from incidents import IncidentService
from monitoring.probe import probe_camera
from websocket.event_dispatcher import dispatch

LOGGER = logging.getLogger(__name__)


class MonitorScheduler:
    """Run camera health checks manually or on a background interval."""

    def __init__(self, interval_seconds=30):
        self.interval_seconds = interval_seconds
        self._started = False
        self._lock = threading.Lock()
        self.last_success_at = None
        self.last_error = None

    def run_once(self):
        now = datetime.now().isoformat(timespec="seconds")
        with self._lock:
            with connect() as db:
                cameras = [row_to_dict(row) for row in db.execute("SELECT * FROM cameras ORDER BY id").fetchall()]
                for camera in cameras:
                    previous_status = camera.get("status")
                    health = probe_camera(camera)
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
        self.last_success_at = now
        self.last_error = None
        return {"ok": True, "checked": len(cameras), "at": now}

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
            except Exception as exc:
                LOGGER.exception("Camera health monitor tick failed")
                self.last_error = str(exc)
            time.sleep(self.interval_seconds)

    def trigger(self):
        return self.run_once()

    def runtime_status(self):
        last = self.last_success_at
        stale = True
        if last:
            try:
                age = (datetime.now() - datetime.fromisoformat(last)).total_seconds()
                stale = age > (self.interval_seconds * 3 + 15)
            except Exception:
                stale = True
        alive = bool(self._started) and last and not stale and not self.last_error
        return {
            "started": self._started,
            "last_success_at": last,
            "last_error": self.last_error,
            "stale": stale,
            "alive": alive,
        }
