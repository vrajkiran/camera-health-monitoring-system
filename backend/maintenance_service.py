"""Asset maintenance mode service for cameras and switches."""

from datetime import datetime

from alerts import send_email_report, send_telegram_message
from database import connect, row_to_dict


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def _is_future(value):
    return bool(value and value > now_text())


class MaintenanceService:
    def start(self, camera_id, reason, technician_name, expected_end_time=None, notes=""):
        return self.start_asset("CAMERA", str(camera_id), reason, technician_name, expected_end_time, notes)

    def complete(self, camera_id, notes="", version=None):
        return self.complete_asset("CAMERA", str(camera_id), notes, version)

    def start_asset(self, asset_type, asset_id, reason, technician_name, expected_end_time=None, notes=""):
        asset_type = (asset_type or "CAMERA").upper()
        started = now_text()
        with connect() as db:
            asset = self._get_asset(db, asset_type, str(asset_id))
            if not asset:
                raise ValueError(f"{asset_type.title()} not found")
            self.expire_due_sessions(db=db)
            active = self._active_session(db, asset_type, str(asset_id))
            if active:
                raise ValueError(f"{asset_type.title()} already has an active maintenance session")
            camera_id = asset.get("camera_id")
            camera_name = asset.get("name")
            cursor = db.execute(
                """
                INSERT INTO maintenance_sessions
                (camera_id, camera_name, maintenance_status, maintenance_reason, technician_name,
                 start_time, expected_end_time, completion_time, notes, created_at, asset_type, asset_id, version)
                VALUES (?, ?, 'ACTIVE', ?, ?, ?, ?, NULL, ?, ?, ?, ?, 1)
                """,
                (camera_id, camera_name, reason, technician_name, started, expected_end_time, notes, started, asset_type, str(asset_id)),
            )
            session_id = cursor.lastrowid
            self._set_asset_maintenance(db, asset_type, str(asset_id), "ACTIVE", reason, technician_name, started, expected_end_time, None, notes)
            self._history(db, session_id, camera_id, asset_type, str(asset_id), "MAINTENANCE_STARTED", f"{asset_type.title()} maintenance started by {technician_name}: {reason}", started)
            return self._get_session(db, session_id)

    def update_session(self, session_id, body):
        updated = now_text()
        with connect() as db:
            session = db.execute("SELECT * FROM maintenance_sessions WHERE id = ?", (session_id,)).fetchone()
            if not session:
                raise ValueError("Maintenance session not found")
            if body.get("version") is not None and int(body.get("version")) != int(session["version"]):
                raise ValueError("This maintenance session was changed by another operator. Refresh and try again.")
            reason = body.get("maintenance_reason") or body.get("reason") or session["maintenance_reason"]
            technician = body.get("technician_name") or session["technician_name"]
            expected = body.get("expected_end_time") if "expected_end_time" in body else session["expected_end_time"]
            notes = body.get("notes") if "notes" in body else session["notes"]
            db.execute(
                """
                UPDATE maintenance_sessions
                SET maintenance_reason = ?, technician_name = ?, expected_end_time = ?, notes = ?, version = version + 1
                WHERE id = ?
                """,
                (reason, technician, expected, notes, session_id),
            )
            asset_type = session["asset_type"] or "CAMERA"
            asset_id = session["asset_id"] or str(session["camera_id"])
            if session["maintenance_status"] == "ACTIVE":
                self._set_asset_maintenance(db, asset_type, asset_id, "ACTIVE", reason, technician, session["start_time"], expected, None, notes)
            self._history(db, session_id, session["camera_id"], asset_type, asset_id, "MAINTENANCE_UPDATED", "Maintenance session details were updated.", updated)
            return self._get_session(db, session_id)

    def complete_asset(self, asset_type, asset_id, notes="", version=None):
        asset_type = (asset_type or "CAMERA").upper()
        completed = now_text()
        with connect() as db:
            session = self._active_session(db, asset_type, str(asset_id))
            if not session:
                raise ValueError("No active maintenance session found")
            if version is not None and int(version) != int(session["version"]):
                raise ValueError("This maintenance session was changed by another operator. Refresh and try again.")
            final_notes = notes or session["notes"] or ""
            db.execute(
                "UPDATE maintenance_sessions SET maintenance_status = 'COMPLETED', completion_time = ?, notes = ?, version = version + 1 WHERE id = ?",
                (completed, final_notes, session["id"]),
            )
            self._set_asset_maintenance(db, asset_type, str(asset_id), "DISABLED", session["maintenance_reason"], session["technician_name"], session["start_time"], session["expected_end_time"], completed, final_notes)
            action = "MAINTENANCE_COMPLETED_EARLY" if _is_future(session["expected_end_time"]) else "MAINTENANCE_COMPLETED"
            self._history(db, session["id"], session["camera_id"], asset_type, str(asset_id), action, "Maintenance completed and normal alerting restored.", completed)
            return self._get_session(db, session["id"])

    def expire_due_sessions(self, db=None):
        if db is None:
            with connect() as conn:
                return self.expire_due_sessions(db=conn)
        completed = now_text()
        expired = []
        rows = db.execute(
            """
            SELECT * FROM maintenance_sessions
            WHERE maintenance_status = 'ACTIVE' AND expected_end_time IS NOT NULL AND expected_end_time <= ?
            """,
            (completed,),
        ).fetchall()
        for row in rows:
            asset_type = row["asset_type"] or "CAMERA"
            asset_id = row["asset_id"] or str(row["camera_id"])
            db.execute("UPDATE maintenance_sessions SET maintenance_status = 'COMPLETED', completion_time = ?, version = version + 1 WHERE id = ?", (completed, row["id"]))
            self._set_asset_maintenance(db, asset_type, asset_id, "DISABLED", row["maintenance_reason"], row["technician_name"], row["start_time"], row["expected_end_time"], completed, row["notes"] or "")
            self._history(db, row["id"], row["camera_id"], asset_type, asset_id, "MAINTENANCE_EXPIRED", "Maintenance window expired; normal alerting restored automatically.", completed)
            self._notify_expired(row, completed)
            expired.append(row["id"])
        return {"expired": expired}

    def summary(self):
        self.expire_due_sessions()
        now = now_text()
        with connect() as db:
            active = db.execute("SELECT COUNT(*) AS total FROM maintenance_sessions WHERE maintenance_status = 'ACTIVE'").fetchone()["total"]
            upcoming = db.execute("SELECT COUNT(*) AS total FROM maintenance_sessions WHERE maintenance_status = 'ACTIVE' AND expected_end_time IS NOT NULL AND expected_end_time >= ?", (now,)).fetchone()["total"]
            expired = db.execute("SELECT COUNT(*) AS total FROM maintenance_sessions WHERE maintenance_status = 'ACTIVE' AND expected_end_time IS NOT NULL AND expected_end_time < ?", (now,)).fetchone()["total"]
            history = db.execute("SELECT * FROM maintenance_history ORDER BY created_at DESC LIMIT 100").fetchall()
        return {"maintenance_cameras": active, "upcoming_maintenance": upcoming, "expired_maintenance": expired, "history": [row_to_dict(row) for row in history]}

    def list_sessions(self, status=None):
        self.expire_due_sessions()
        with connect() as db:
            if status:
                rows = db.execute("SELECT * FROM maintenance_sessions WHERE maintenance_status = ? ORDER BY start_time DESC", (status,)).fetchall()
            else:
                rows = db.execute("SELECT * FROM maintenance_sessions ORDER BY start_time DESC LIMIT 300").fetchall()
        return [row_to_dict(row) for row in rows]

    def get_session(self, session_id):
        with connect() as db:
            return self._get_session(db, session_id)

    def _get_session(self, db, session_id):
        row = db.execute("SELECT * FROM maintenance_sessions WHERE id = ?", (session_id,)).fetchone()
        return row_to_dict(row) if row else None

    def _get_asset(self, db, asset_type, asset_id):
        if asset_type == "SWITCH":
            row = db.execute("SELECT * FROM switches WHERE switch_id = ?", (asset_id,)).fetchone()
            if not row:
                camera = db.execute("SELECT switch_id, switch_ip, MIN(location) AS location FROM cameras WHERE switch_id = ? GROUP BY switch_id, switch_ip", (asset_id,)).fetchone()
                if not camera:
                    return None
                return {"camera_id": None, "name": camera["switch_id"], "switch_id": camera["switch_id"], "ip_address": camera["switch_ip"], "location": camera["location"]}
            item = row_to_dict(row)
            item["camera_id"] = None
            item["name"] = item.get("switch_name") or item.get("switch_id")
            return item
        row = db.execute("SELECT * FROM cameras WHERE id = ?", (int(asset_id),)).fetchone()
        if not row:
            return None
        item = row_to_dict(row)
        item["camera_id"] = item["id"]
        return item

    def _active_session(self, db, asset_type, asset_id):
        row = db.execute(
            """
            SELECT * FROM maintenance_sessions
            WHERE maintenance_status = 'ACTIVE' AND asset_type = ? AND COALESCE(asset_id, CAST(camera_id AS TEXT)) = ?
            ORDER BY start_time DESC LIMIT 1
            """,
            (asset_type, str(asset_id)),
        ).fetchone()
        if not row and asset_type == "CAMERA":
            row = db.execute("SELECT * FROM maintenance_sessions WHERE maintenance_status = 'ACTIVE' AND camera_id = ? ORDER BY start_time DESC LIMIT 1", (int(asset_id),)).fetchone()
        return row

    def _set_asset_maintenance(self, db, asset_type, asset_id, status, reason, technician, start_time, expected_end_time, completion_time, notes):
        if asset_type == "SWITCH":
            db.execute(
                """
                UPDATE switches
                SET maintenance_status = ?, maintenance_reason = ?, maintenance_technician = ?,
                    maintenance_start_time = ?, maintenance_expected_end_time = ?, maintenance_completion_time = ?, maintenance_notes = ?, updated_at = ?
                WHERE switch_id = ?
                """,
                (status, reason or "", technician or "", start_time, expected_end_time, completion_time, notes or "", now_text(), str(asset_id)),
            )
        else:
            db.execute(
                """
                UPDATE cameras
                SET maintenance_status = ?, maintenance_reason = ?, maintenance_technician = ?,
                    maintenance_start_time = ?, maintenance_expected_end_time = ?, maintenance_completion_time = ?, maintenance_notes = ?
                WHERE id = ?
                """,
                (status, reason or "", technician or "", start_time, expected_end_time, completion_time, notes or "", int(asset_id)),
            )

    def _history(self, db, session_id, camera_id, asset_type, asset_id, action, description, created_at):
        db.execute(
            "INSERT INTO maintenance_history (session_id, camera_id, action, description, created_at, asset_type, asset_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, camera_id, action, description, created_at, asset_type, str(asset_id)),
        )
        db.execute("INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)", (action, description, created_at))

    def _notify_expired(self, session, completed):
        asset_name = session["camera_name"] or session["asset_id"] or "Asset"
        message = (
            "MAINTENANCE WINDOW COMPLETED\n\n"
            f"Asset: {asset_name}\n"
            f"Technician: {session['technician_name']}\n"
            f"Reason: {session['maintenance_reason']}\n"
            f"Completed: {completed}\n"
            "Status: Normal monitoring and alerting restored."
        )
        try:
            send_telegram_message(message)
        except Exception:
            pass
        try:
            send_email_report("Maintenance Window Completed", message)
        except Exception:
            pass
