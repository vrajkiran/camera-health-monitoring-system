"""Switch asset service backed by camera inventory."""

from datetime import datetime
from database import connect, row_to_dict


def now_text():
    return datetime.now().isoformat(timespec="seconds")


class SwitchService:
    def list_switches(self):
        with connect() as db:
            self._backfill(db)
            rows = db.execute("SELECT * FROM switches ORDER BY switch_id").fetchall()
            result = []
            for row in rows:
                item = row_to_dict(row)
                cams = db.execute("SELECT * FROM cameras WHERE switch_id = ? ORDER BY name", (item["switch_id"],)).fetchall()
                cameras = [row_to_dict(c) for c in cams]
                item["connected_cameras"] = len(cameras)
                item["cameras"] = cameras
                item["avg_latency_ms"] = round(sum([c["latency_ms"] for c in cameras if c["latency_ms"] is not None]) / max(1, len([c for c in cameras if c["latency_ms"] is not None])), 1) if any(c["latency_ms"] is not None for c in cameras) else None
                result.append(item)
            return result

    def get_switch(self, switch_id):
        with connect() as db:
            self._backfill(db)
            row = db.execute("SELECT * FROM switches WHERE switch_id = ?", (switch_id,)).fetchone()
            return row_to_dict(row) if row else None

    def update_switch(self, switch_id, body):
        updated = now_text()
        with connect() as db:
            self._backfill(db)
            db.execute(
                """
                UPDATE switches SET switch_name = ?, ip_address = ?, location = ?, updated_at = ?
                WHERE switch_id = ?
                """,
                (body.get("switch_name") or switch_id, body.get("ip_address") or '', body.get("location") or '', updated, switch_id),
            )
            db.execute("INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)", ("SWITCH_UPDATED", f"Switch {switch_id} was updated.", updated))
        return self.get_switch(switch_id)

    def _backfill(self, db):
        rows = db.execute("""
            SELECT switch_id, COALESCE(NULLIF(switch_ip, ''), '') AS switch_ip, MIN(location) AS location,
                   COUNT(*) AS total, SUM(CASE WHEN status = 'ONLINE' THEN 1 ELSE 0 END) AS online_count, AVG(latency_ms) AS avg_latency
            FROM cameras GROUP BY switch_id, switch_ip
        """).fetchall()
        now = now_text()
        for row in rows:
            total = row["total"] or 0
            online = row["online_count"] or 0
            status = 'OFFLINE' if total and online == 0 else ('UNSTABLE' if online < total else 'ONLINE')
            health = int((online / total) * 100) if total else 100
            packet_loss = 100 if status == 'OFFLINE' else (25 if status == 'UNSTABLE' else 0)
            db.execute("""
                INSERT INTO switches (switch_id, switch_name, ip_address, location, status, packet_loss_pct, avg_latency_ms, health_score, uptime_pct, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 100, ?, ?)
                ON CONFLICT(switch_id) DO UPDATE SET status=excluded.status, packet_loss_pct=excluded.packet_loss_pct,
                    avg_latency_ms=excluded.avg_latency_ms, health_score=excluded.health_score, updated_at=excluded.updated_at
            """, (row["switch_id"], row["switch_id"], row["switch_ip"], row["location"] or '', status, packet_loss, row["avg_latency"], health, now, now))
