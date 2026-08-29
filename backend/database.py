import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta

from config import BASE_DIR, DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    ip_address TEXT NOT NULL UNIQUE,
    switch_id TEXT NOT NULL,
    switch_ip TEXT NOT NULL DEFAULT '',
    rtsp_url TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ONLINE', 'OFFLINE', 'UNSTABLE', 'STREAM_FAILURE')),
    last_checked TEXT NOT NULL,
    latency_ms INTEGER,
    stream_status TEXT NOT NULL,
    stream_response_ms INTEGER,
    last_stream_check TEXT
);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER,
    camera_name TEXT NOT NULL,
    alert_type TEXT NOT NULL CHECK(alert_type IN ('EMAIL', 'TELEGRAM')),
    message TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(camera_id) REFERENCES cameras(id)
);
CREATE TABLE IF NOT EXISTS downtime_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    camera_name TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    failure_time TEXT NOT NULL,
    recovery_time TEXT,
    duration_minutes INTEGER,
    FOREIGN KEY(camera_id) REFERENCES cameras(id)
);
CREATE TABLE IF NOT EXISTS ping_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    response_time_ms INTEGER,
    packet_loss_pct INTEGER NOT NULL DEFAULT 0,
    recorded_at TEXT NOT NULL,
    is_anomaly INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(camera_id) REFERENCES cameras(id)
);
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK(id = 1),
    user_name TEXT NOT NULL DEFAULT 'UCEK-JNTUK Admin',
    user_role TEXT NOT NULL DEFAULT 'Campus Surveillance Administrator',
    user_email TEXT NOT NULL DEFAULT '',
    email_recipients TEXT NOT NULL DEFAULT '',
    telegram_bot_token TEXT NOT NULL DEFAULT '',
    telegram_chat_id TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'VIEWER',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    last_login TEXT
);CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    risk_score INTEGER,
    risk_level TEXT,
    predicted_failure_window TEXT,
    recommended_action TEXT,
    features_snapshot TEXT,
    created_at TEXT,
    FOREIGN KEY (camera_id) REFERENCES cameras(id)
);
CREATE TABLE IF NOT EXISTS diagnosis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER,
    camera_name TEXT NOT NULL,
    severity TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    confidence INTEGER NOT NULL,
    recommended_solution TEXT NOT NULL,
    source_event TEXT NOT NULL,
    resolution_status TEXT NOT NULL DEFAULT 'OPEN',
    created_at TEXT NOT NULL,
    FOREIGN KEY(camera_id) REFERENCES cameras(id)
);
CREATE TABLE IF NOT EXISTS notification_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_type TEXT NOT NULL,
    recipient TEXT NOT NULL,
    status TEXT NOT NULL,
    delivery_result TEXT NOT NULL,
    camera_id INTEGER,
    camera_name TEXT,
    severity TEXT,
    diagnosis TEXT,
    confidence INTEGER,
    recommended_action TEXT,
    resolution_status TEXT NOT NULL DEFAULT 'OPEN',
    created_at TEXT NOT NULL,
    FOREIGN KEY(camera_id) REFERENCES cameras(id)
);CREATE TABLE IF NOT EXISTS incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    camera_name TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('NEW', 'NOTIFIED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED')),
    diagnosis TEXT NOT NULL,
    confidence INTEGER NOT NULL,
    recommendation TEXT NOT NULL,
    first_detected TEXT NOT NULL,
    last_notification TEXT,
    next_notification TEXT,
    notification_count INTEGER NOT NULL DEFAULT 0,
    acknowledged INTEGER NOT NULL DEFAULT 0,
    acknowledged_by TEXT,
    acknowledged_time TEXT,
    resolved_time TEXT,
    downtime INTEGER,
    FOREIGN KEY(camera_id) REFERENCES cameras(id)
);
CREATE TABLE IF NOT EXISTS incident_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    notification_type TEXT NOT NULL,
    recipient TEXT NOT NULL,
    sent_time TEXT NOT NULL,
    delivery_status TEXT NOT NULL,
    delivery_result TEXT NOT NULL,
    reminder_number INTEGER NOT NULL DEFAULT 0,
    telegram_message_id TEXT,
    FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
);
CREATE TABLE IF NOT EXISTS incident_state_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    from_status TEXT,
    to_status TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
);
CREATE TABLE IF NOT EXISTS incident_runtime_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS maintenance_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    camera_name TEXT NOT NULL,
    maintenance_status TEXT NOT NULL DEFAULT 'ACTIVE',
    maintenance_reason TEXT NOT NULL,
    technician_name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    expected_end_time TEXT,
    completion_time TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(camera_id) REFERENCES cameras(id)
);
CREATE TABLE IF NOT EXISTS maintenance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    camera_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES maintenance_sessions(id),
    FOREIGN KEY(camera_id) REFERENCES cameras(id)
);
CREATE TABLE IF NOT EXISTS ai_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    camera_id INTEGER,
    predicted_cause TEXT NOT NULL,
    actual_cause TEXT,
    diagnosis_correct INTEGER NOT NULL,
    resolution_notes TEXT,
    operator TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
);
CREATE TABLE IF NOT EXISTS root_cause_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cause TEXT NOT NULL,
    incident_count INTEGER NOT NULL DEFAULT 0,
    avg_downtime_minutes REAL,
    last_updated TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS monthly_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_period TEXT NOT NULL,
    report_date TEXT NOT NULL,
    generation_time TEXT NOT NULL,
    generated_by TEXT NOT NULL DEFAULT 'System',
    html_copy TEXT,
    pdf_copy TEXT,
    excel_copy TEXT,
    summary_json TEXT,
    archived INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT NOT NULL,
    reporting_period TEXT NOT NULL,
    generation_time TEXT NOT NULL,
    generated_by TEXT NOT NULL DEFAULT 'System',
    html_copy TEXT,
    pdf_copy TEXT,
    excel_copy TEXT,
    summary_json TEXT,
    archived INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS escalations (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    camera_name TEXT,
    alert_type TEXT,
    stage INTEGER DEFAULT 1,
    triggered_at TEXT,
    completed_at TEXT,
    status TEXT DEFAULT 'ACTIVE'
);"""

DEMO_CAMERAS = [
    ("Main Gate CAM-01", "Main Gate", "192.168.10.21", "SW-A", "192.168.10.2", "rtsp://192.168.10.21/live", "ONLINE", 18, "Reachable; RTSP stream healthy", 42),
    ("Library Entrance CAM-02", "Library Block", "192.168.10.34", "SW-B", "192.168.10.3", "rtsp://192.168.10.34/live", "UNSTABLE", 184, "High latency", 86),
    ("Canteen Corridor CAM-03", "Student Center", "192.168.10.49", "SW-C", "192.168.10.4", "rtsp://192.168.10.49/live", "ONLINE", 22, "Reachable; RTSP stream healthy", 51),
    ("Admin Office CAM-04", "Admin Block", "192.168.10.58", "SW-A", "192.168.10.2", "rtsp://192.168.10.58/live", "OFFLINE", None, "No ping response", None),
    ("Parking East CAM-05", "Parking Area", "192.168.10.71", "SW-D", "192.168.10.5", "rtsp://192.168.10.71/live", "ONLINE", 31, "Reachable; RTSP stream healthy", 47),
    ("Lab Floor 2 CAM-06", "Engineering Block", "192.168.10.87", "SW-B", "192.168.10.3", "rtsp://192.168.10.87/live", "STREAM_FAILURE", 46, "Ping OK; RTSP stream unavailable", None),
    ("ECE Block Entrance CAM-07", "ECE Block", "192.168.10.101", "SW-E", "192.168.10.6", "rtsp://192.168.10.101/live", "ONLINE", 29, "Reachable; RTSP stream healthy", 44),
    ("Mechanical Workshop CAM-08", "Mechanical Block", "192.168.10.102", "SW-F", "192.168.10.7", "rtsp://192.168.10.102/live", "ONLINE", 34, "Reachable; RTSP stream healthy", 52),
    ("Civil Lab Corridor CAM-09", "Civil Block", "192.168.10.103", "SW-G", "192.168.10.8", "rtsp://192.168.10.103/live", "UNSTABLE", 162, "Intermittent packet delay", 78),
    ("Exam Cell CAM-10", "Administrative Block", "192.168.10.104", "SW-A", "192.168.10.2", "rtsp://192.168.10.104/live", "ONLINE", 26, "Reachable; RTSP stream healthy", 39),
    ("Principal Office CAM-11", "Administrative Block", "192.168.10.105", "SW-A", "192.168.10.2", "rtsp://192.168.10.105/live", "ONLINE", 24, "Reachable; RTSP stream healthy", 36),
    ("Boys Hostel Gate CAM-12", "Boys Hostel", "192.168.10.106", "SW-H", "192.168.10.9", "rtsp://192.168.10.106/live", "OFFLINE", None, "No ping response", None),
    ("Girls Hostel Gate CAM-13", "Girls Hostel", "192.168.10.107", "SW-I", "192.168.10.10", "rtsp://192.168.10.107/live", "ONLINE", 37, "Reachable; RTSP stream healthy", 58),
    ("Seminar Hall CAM-14", "Seminar Hall", "192.168.10.108", "SW-J", "192.168.10.11", "rtsp://192.168.10.108/live", "ONLINE", 33, "Reachable; RTSP stream healthy", 45),
    ("Server Room CAM-15", "IT Center", "192.168.10.109", "SW-K", "192.168.10.12", "rtsp://192.168.10.109/live", "STREAM_FAILURE", 41, "Ping OK; RTSP authentication failure", None),
    ("Library Reading Hall CAM-16", "Library Block", "192.168.10.110", "SW-B", "192.168.10.3", "rtsp://192.168.10.110/live", "ONLINE", 28, "Reachable; RTSP stream healthy", 43),
    ("Sports Ground CAM-17", "Sports Ground", "192.168.10.111", "SW-L", "192.168.10.13", "rtsp://192.168.10.111/live", "UNSTABLE", 171, "High latency", 82),
    ("Auditorium Lobby CAM-18", "Auditorium", "192.168.10.112", "SW-M", "192.168.10.14", "rtsp://192.168.10.112/live", "ONLINE", 35, "Reachable; RTSP stream healthy", 48),
    ("Chemistry Lab CAM-19", "Science Block", "192.168.10.113", "SW-N", "192.168.10.15", "rtsp://192.168.10.113/live", "ONLINE", 39, "Reachable; RTSP stream healthy", 56),
    ("Physics Lab CAM-20", "Science Block", "192.168.10.114", "SW-N", "192.168.10.15", "rtsp://192.168.10.114/live", "ONLINE", 32, "Reachable; RTSP stream healthy", 49),
    ("Bus Bay CAM-21", "Transport Area", "192.168.10.115", "SW-O", "192.168.10.16", "rtsp://192.168.10.115/live", "ONLINE", 43, "Reachable; RTSP stream healthy", 62),
    ("Back Gate CAM-22", "Rear Entrance", "192.168.10.116", "SW-P", "192.168.10.17", "rtsp://192.168.10.116/live", "OFFLINE", None, "No ping response", None),
    ("Placement Cell CAM-23", "Placement Block", "192.168.10.117", "SW-Q", "192.168.10.18", "rtsp://192.168.10.117/live", "ONLINE", 27, "Reachable; RTSP stream healthy", 40),
    ("Academic Section CAM-24", "Academic Section", "192.168.10.118", "SW-R", "192.168.10.19", "rtsp://192.168.10.118/live", "ONLINE", 30, "Reachable; RTSP stream healthy", 46),
    ("Central Corridor CAM-25", "Main Academic Block", "192.168.10.119", "SW-S", "192.168.10.20", "rtsp://192.168.10.119/live", "ONLINE", 36, "Reachable; RTSP stream healthy", 50),
]
@contextmanager
def connect():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()

def row_to_dict(row):
    return {key: row[key] for key in row.keys()}

def _camera_columns(db):
    return [row["name"] for row in db.execute("PRAGMA table_info(cameras)").fetchall()]

def _camera_schema_allows_stream_failure(db):
    row = db.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'cameras'").fetchone()
    return bool(row and row["sql"] and "STREAM_FAILURE" in row["sql"])

def _rebuild_cameras_table(db):
    columns = _camera_columns(db)
    if not columns:
        return
    db.execute("ALTER TABLE cameras RENAME TO cameras_old")
    db.execute(
        """
        CREATE TABLE cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            ip_address TEXT NOT NULL UNIQUE,
            switch_id TEXT NOT NULL,
            switch_ip TEXT NOT NULL DEFAULT '',
            rtsp_url TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('ONLINE', 'OFFLINE', 'UNSTABLE', 'STREAM_FAILURE')),
            last_checked TEXT NOT NULL,
            latency_ms INTEGER,
            stream_status TEXT NOT NULL,
            stream_response_ms INTEGER,
            last_stream_check TEXT,
            maintenance_status TEXT NOT NULL DEFAULT 'DISABLED',
            maintenance_reason TEXT NOT NULL DEFAULT '',
            maintenance_technician TEXT NOT NULL DEFAULT '',
            maintenance_start_time TEXT,
            maintenance_expected_end_time TEXT,
            maintenance_completion_time TEXT,
            maintenance_notes TEXT NOT NULL DEFAULT ''
        )
        """
    )
    select_exprs = []
    for column in ("id", "name", "location", "ip_address", "switch_id", "switch_ip", "rtsp_url", "status", "last_checked", "latency_ms", "stream_status", "stream_response_ms", "last_stream_check"):
        if column in columns:
            select_exprs.append(column)
        elif column == "switch_ip":
            select_exprs.append("'' AS switch_ip")
        elif column == "stream_status":
            select_exprs.append("'Reachable' AS stream_status")
        elif column in ("stream_response_ms", "last_stream_check"):
            select_exprs.append(f"NULL AS {column}")
    db.execute(
        f"INSERT INTO cameras ({', '.join(['id', 'name', 'location', 'ip_address', 'switch_id', 'switch_ip', 'rtsp_url', 'status', 'last_checked', 'latency_ms', 'stream_status', 'stream_response_ms', 'last_stream_check'])}) "
        f"SELECT {', '.join(select_exprs)} FROM cameras_old"
    )
    db.execute("DROP TABLE cameras_old")


def _ensure_column(db, table, column, definition):
    columns = [row["name"] for row in db.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

def migrate(db):
    _ensure_column(db, "cameras", "maintenance_status", "TEXT NOT NULL DEFAULT 'DISABLED'")
    _ensure_column(db, "cameras", "maintenance_reason", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(db, "cameras", "maintenance_technician", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(db, "cameras", "maintenance_start_time", "TEXT")
    _ensure_column(db, "cameras", "maintenance_expected_end_time", "TEXT")
    _ensure_column(db, "cameras", "maintenance_completion_time", "TEXT")
    _ensure_column(db, "cameras", "maintenance_notes", "TEXT NOT NULL DEFAULT ''")
    columns = _camera_columns(db)
    if columns and "switch_ip" not in columns:
        db.execute("ALTER TABLE cameras ADD COLUMN switch_ip TEXT NOT NULL DEFAULT ''")
    columns = _camera_columns(db)
    if columns and "stream_status" not in columns:
        db.execute("ALTER TABLE cameras ADD COLUMN stream_status TEXT NOT NULL DEFAULT 'Reachable'")
    columns = _camera_columns(db)
    if columns and "stream_response_ms" not in columns:
        db.execute("ALTER TABLE cameras ADD COLUMN stream_response_ms INTEGER")
    columns = _camera_columns(db)
    if columns and "last_stream_check" not in columns:
        db.execute("ALTER TABLE cameras ADD COLUMN last_stream_check TEXT")
    if _camera_columns(db) and not _camera_schema_allows_stream_failure(db):
        _rebuild_cameras_table(db)

def ensure_settings(db):
    now = datetime.now().isoformat(timespec="seconds")
    db.execute(
        """
        INSERT OR IGNORE INTO settings
        (id, user_name, user_role, user_email, email_recipients, telegram_bot_token, telegram_chat_id, updated_at)
        VALUES (1, 'UCEK-JNTUK Admin', 'Campus Surveillance Administrator', '', '', '', '', ?)
        """,
        (now,),
    )


def ensure_default_admin(db):
    from auth import hash_password
    now = datetime.now().isoformat(timespec="seconds")
    count = db.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
    if count:
        return
    db.execute(
        """
        INSERT INTO users (username, full_name, email, password_hash, role, is_active, created_at, last_login)
        VALUES (?, ?, ?, ?, ?, 1, ?, NULL)
        """,
        ("admin", "UCEK Admin", "admin@ucek.ac.in", hash_password("Admin@1234"), "ADMINISTRATOR", now),
    )


def ensure_demo_cameras(db):
    """Backfill bundled demo cameras without deleting user-created records."""
    now = datetime.now()
    existing_ips = {row["ip_address"] for row in db.execute("SELECT ip_address FROM cameras").fetchall()}
    for index, camera in enumerate(DEMO_CAMERAS):
        if camera[2] in existing_ips:
            continue
        checked_at = (now - timedelta(minutes=index + 1)).isoformat(timespec="seconds")
        cursor = db.execute(
            """
            INSERT INTO cameras
            (name, location, ip_address, switch_id, switch_ip, rtsp_url, status, last_checked, latency_ms, stream_status, stream_response_ms, last_stream_check)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (*camera[:7], checked_at, camera[7], camera[8], camera[9], checked_at),
        )
        camera_id = cursor.lastrowid
        for offset in range(20, 0, -1):
            latency = None if camera[6] == "OFFLINE" else max(18, (camera[7] or 30) + (offset % 5))
            db.execute(
                "INSERT INTO ping_history (camera_id, response_time_ms, packet_loss_pct, recorded_at, is_anomaly) VALUES (?, ?, ?, ?, ?)",
                (camera_id, latency, 100 if camera[6] == "OFFLINE" else 0, (now - timedelta(minutes=offset)).isoformat(timespec="seconds"), 1 if camera[6] in ("UNSTABLE", "STREAM_FAILURE") and offset < 4 else 0),
            )

def run_enterprise_migrations():
    try:
        import importlib.util
        migration_path = BASE_DIR / "backend" / "migrations" / "001_enterprise_assets.py"
        if not migration_path.exists():
            migration_path = BASE_DIR / "migrations" / "001_enterprise_assets.py"
        if migration_path.exists():
            spec = importlib.util.spec_from_file_location("enterprise_assets_migration", migration_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.run()
    except Exception as exc:
        print(f"Enterprise migration skipped: {exc}")

def init_db():
    with connect() as db:
        db.executescript(SCHEMA)
        migrate(db)
        ensure_settings(db)
        ensure_default_admin(db)
        count = db.execute("SELECT COUNT(*) AS total FROM cameras").fetchone()["total"]
        if count:
            ensure_demo_cameras(db)
        else:
            now = datetime.now()
            for index, camera in enumerate(DEMO_CAMERAS):
                checked_at = (now - timedelta(minutes=index + 1)).isoformat(timespec="seconds")
                db.execute(
                    """
                    INSERT INTO cameras
                    (name, location, ip_address, switch_id, switch_ip, rtsp_url, status, last_checked, latency_ms, stream_status, stream_response_ms, last_stream_check)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (*camera[:7], checked_at, camera[7], camera[8], camera[9], checked_at),
                )
            alerts = [
                (4, "Admin Office CAM-04", "EMAIL", "Camera is unreachable. Check power supply and network cable.", now - timedelta(minutes=4), 0),
                (2, "Library Entrance CAM-02", "TELEGRAM", "ML module detected abnormal ping latency for three checks.", now - timedelta(minutes=9), 0),
                (6, "Lab Floor 2 CAM-06", "EMAIL", "Camera ping is reachable, but the RTSP stream is unavailable.", now - timedelta(minutes=15), 1),
            ]
            for alert in alerts:
                db.execute("INSERT INTO alerts (camera_id, camera_name, alert_type, message, sent_at, is_read) VALUES (?, ?, ?, ?, ?, ?)", (alert[0], alert[1], alert[2], alert[3], alert[4].isoformat(timespec="seconds"), alert[5]))
            logs = [
                (4, "Admin Office CAM-04", "POWER_OR_CABLE", now - timedelta(minutes=6), None, None),
                (2, "Library Entrance CAM-02", "UNSTABLE_CONNECTION_ML", now - timedelta(minutes=12), None, None),
                (6, "Lab Floor 2 CAM-06", "RTSP_STREAM_FAILURE", now - timedelta(minutes=18), None, None),
            ]
            for log in logs:
                db.execute("INSERT INTO downtime_logs (camera_id, camera_name, root_cause, failure_time, recovery_time, duration_minutes) VALUES (?, ?, ?, ?, ?, ?)", (log[0], log[1], log[2], log[3].isoformat(timespec="seconds"), log[4], log[5]))
            for camera_id in range(1, 7):
                for offset in range(20, 0, -1):
                    latency = 18 + camera_id * 3 + (offset % 5)
                    db.execute(
                        "INSERT INTO ping_history (camera_id, response_time_ms, packet_loss_pct, recorded_at, is_anomaly) VALUES (?, ?, ?, ?, ?)",
                        (camera_id, None if camera_id == 4 else latency, 100 if camera_id == 4 else 0, (now - timedelta(minutes=offset)).isoformat(timespec="seconds"), 1 if camera_id in (2, 6) and offset < 4 else 0),
                    )
            db.execute("INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)", ("SYSTEM_READY", "Demo database initialized for UCEK-JNTUK Camera Health Monitoring System.", now.isoformat(timespec="seconds")))
    run_enterprise_migrations()

def reset_demo_data():
    with connect() as db:
        db.executescript(SCHEMA)
        migrate(db)
        ensure_settings(db)
        ensure_default_admin(db)
        for table in ("daily_reports", "monthly_reports", "root_cause_statistics", "ai_feedback", "maintenance_history", "maintenance_sessions", "incident_runtime_state", "incident_state_log", "incident_notifications", "incidents", "notification_history", "diagnosis_history", "predictions", "escalations", "ping_history", "downtime_logs", "alerts", "cameras", "user_activity"):
            db.execute(f"DELETE FROM {table}")
        db.execute("DELETE FROM sqlite_sequence WHERE name IN ('cameras', 'alerts', 'downtime_logs', 'ping_history', 'user_activity', 'predictions', 'escalations', 'diagnosis_history', 'notification_history', 'incidents', 'incident_notifications', 'incident_state_log', 'maintenance_sessions', 'maintenance_history', 'ai_feedback', 'root_cause_statistics', 'monthly_reports', 'daily_reports')")
    init_db()


def backup_database():
    """Create a rolling SQLite database backup and keep only the latest seven files."""
    backups_dir = BASE_DIR / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backups_dir / f"backup_{timestamp}.db"
    if DATABASE_PATH.exists():
        shutil.copy2(DATABASE_PATH, backup_path)
    backups = sorted(backups_dir.glob("backup_*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
    for old_path in backups[7:]:
        try:
            old_path.unlink()
        except Exception:
            pass
    return str(backup_path)


