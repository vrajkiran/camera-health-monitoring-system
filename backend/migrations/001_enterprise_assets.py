"""Idempotent migration for enterprise assets and maintenance."""

from datetime import datetime
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import DATABASE_PATH


def ensure_column(db, table, column, definition):
    cols = [row[1] for row in db.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in cols:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def run():
    now = datetime.now().isoformat(timespec="seconds")
    db = sqlite3.connect(DATABASE_PATH)
    try:
        db.execute("""
        CREATE TABLE IF NOT EXISTS switches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            switch_id TEXT NOT NULL UNIQUE,
            switch_name TEXT NOT NULL,
            ip_address TEXT NOT NULL DEFAULT '',
            location TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'ONLINE',
            packet_loss_pct INTEGER NOT NULL DEFAULT 0,
            avg_latency_ms REAL,
            health_score INTEGER NOT NULL DEFAULT 100,
            uptime_pct REAL NOT NULL DEFAULT 100,
            cpu_pct REAL,
            temperature_c REAL,
            maintenance_status TEXT NOT NULL DEFAULT 'DISABLED',
            maintenance_reason TEXT NOT NULL DEFAULT '',
            maintenance_technician TEXT NOT NULL DEFAULT '',
            maintenance_start_time TEXT,
            maintenance_expected_end_time TEXT,
            maintenance_completion_time TEXT,
            maintenance_notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        ensure_column(db, "maintenance_sessions", "asset_type", "TEXT NOT NULL DEFAULT 'CAMERA'")
        ensure_column(db, "maintenance_sessions", "asset_id", "TEXT")
        ensure_column(db, "maintenance_sessions", "version", "INTEGER NOT NULL DEFAULT 1")
        ensure_column(db, "maintenance_history", "asset_type", "TEXT NOT NULL DEFAULT 'CAMERA'")
        ensure_column(db, "maintenance_history", "asset_id", "TEXT")
        ensure_column(db, "cameras", "maintenance_status", "TEXT NOT NULL DEFAULT 'DISABLED'")
        ensure_column(db, "cameras", "maintenance_reason", "TEXT NOT NULL DEFAULT ''")
        ensure_column(db, "cameras", "maintenance_technician", "TEXT NOT NULL DEFAULT ''")
        ensure_column(db, "cameras", "maintenance_start_time", "TEXT")
        ensure_column(db, "cameras", "maintenance_expected_end_time", "TEXT")
        ensure_column(db, "cameras", "maintenance_completion_time", "TEXT")
        ensure_column(db, "cameras", "maintenance_notes", "TEXT NOT NULL DEFAULT ''")
        rows = db.execute("""
            SELECT switch_id, COALESCE(NULLIF(switch_ip, ''), '') AS switch_ip,
                   MIN(location) AS location,
                   COUNT(*) AS total,
                   SUM(CASE WHEN status = 'ONLINE' THEN 1 ELSE 0 END) AS online_count,
                   AVG(latency_ms) AS avg_latency
            FROM cameras
            GROUP BY switch_id, switch_ip
        """).fetchall()
        for switch_id, switch_ip, location, total, online_count, avg_latency in rows:
            status = 'OFFLINE' if total and online_count == 0 else ('UNSTABLE' if online_count < total else 'ONLINE')
            health = int((online_count or 0) / total * 100) if total else 100
            packet_loss = 100 if status == 'OFFLINE' else (25 if status == 'UNSTABLE' else 0)
            db.execute("""
                INSERT INTO switches
                (switch_id, switch_name, ip_address, location, status, packet_loss_pct, avg_latency_ms, health_score, uptime_pct, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(switch_id) DO UPDATE SET
                    ip_address = excluded.ip_address,
                    location = excluded.location,
                    status = excluded.status,
                    packet_loss_pct = excluded.packet_loss_pct,
                    avg_latency_ms = excluded.avg_latency_ms,
                    health_score = excluded.health_score,
                    updated_at = excluded.updated_at
            """, (switch_id, switch_id, switch_ip, location or '', status, packet_loss, avg_latency, health, 100.0, now, now))
        db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    run()
