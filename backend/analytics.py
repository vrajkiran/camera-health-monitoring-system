"""Operational analytics for camera uptime, reliability and downtime trends."""

from datetime import date, datetime, timedelta

from database import connect, row_to_dict


def _camera_metrics(db, camera):
    camera_id = camera["id"]
    ping = db.execute(
        """
        SELECT COUNT(*) AS total_checks,
               SUM(CASE WHEN response_time_ms IS NOT NULL THEN 1 ELSE 0 END) AS online_checks,
               AVG(response_time_ms) AS avg_latency
        FROM ping_history WHERE camera_id = ?
        """,
        (camera_id,),
    ).fetchone()
    logs = db.execute(
        """
        SELECT COUNT(*) AS incident_count, AVG(duration_minutes) AS mttr_minutes
        FROM downtime_logs WHERE camera_id = ?
        """,
        (camera_id,),
    ).fetchone()
    total_checks = ping["total_checks"] or 0
    online_checks = ping["online_checks"] or 0
    uptime_pct = round((online_checks / total_checks) * 100, 2) if total_checks else 0
    avg_latency = round(ping["avg_latency"], 1) if ping["avg_latency"] is not None else None
    incident_count = logs["incident_count"] or 0
    mttr_minutes = round(logs["mttr_minutes"], 1) if logs["mttr_minutes"] is not None else None
    mttr_factor = min(1, 10 / (mttr_minutes + 1) if mttr_minutes else 1)
    incident_factor = min(1, 1 / (incident_count + 1))
    reliability_index = round((0.6 * (uptime_pct / 100) + 0.2 * mttr_factor + 0.2 * incident_factor) * 100, 1)
    return {
        "camera_id": camera_id,
        "name": camera.get("name") or "Camera",
        "location": camera.get("location") or "",
        "status": camera.get("status") or "UNKNOWN",
        "uptime_pct": uptime_pct,
        "avg_latency": avg_latency,
        "incident_count": incident_count,
        "mttr_minutes": mttr_minutes,
        "reliability_index": reliability_index,
    }


def get_camera_analytics():
    """Return per-camera reliability analytics sorted from worst to best."""
    try:
        with connect() as db:
            cameras = [row_to_dict(row) for row in db.execute("SELECT * FROM cameras ORDER BY id").fetchall()]
            results = [_camera_metrics(db, camera) for camera in cameras]
        return sorted(results, key=lambda item: item["reliability_index"])
    except Exception:
        return []


def get_downtime_trend():
    """Return daily downtime incident counts for the last 30 days."""
    today = date.today()
    start = today - timedelta(days=29)
    trend = {str(start + timedelta(days=offset)): 0 for offset in range(30)}
    try:
        with connect() as db:
            rows = db.execute(
                """
                SELECT DATE(failure_time) AS day, COUNT(*) AS incident_count
                FROM downtime_logs
                WHERE DATE(failure_time) >= DATE(?)
                GROUP BY DATE(failure_time)
                """,
                (start.isoformat(),),
            ).fetchall()
        for row in rows:
            if row["day"] in trend:
                trend[row["day"]] = row["incident_count"]
    except Exception:
        pass
    return [{"date": day, "incident_count": count} for day, count in trend.items()]


def get_system_summary():
    """Return aggregate system health and reliability highlights."""
    try:
        analytics = get_camera_analytics()
        with connect() as db:
            status = db.execute(
                """
                SELECT COUNT(*) AS total_cameras,
                       SUM(CASE WHEN status = 'ONLINE' THEN 1 ELSE 0 END) AS online_count,
                       SUM(CASE WHEN status = 'OFFLINE' THEN 1 ELSE 0 END) AS offline_count,
                       SUM(CASE WHEN status = 'UNSTABLE' THEN 1 ELSE 0 END) AS unstable_count
                FROM cameras
                """
            ).fetchone()
            cutoff = (datetime.now() - timedelta(days=30)).isoformat(timespec="seconds")
            incidents = db.execute("SELECT COUNT(*) AS total FROM downtime_logs WHERE failure_time >= ?", (cutoff,)).fetchone()["total"]
        total = status["total_cameras"] or 0
        overall_uptime = round(sum(item["uptime_pct"] for item in analytics) / len(analytics), 2) if analytics else 0
        best = max(analytics, key=lambda item: item["reliability_index"], default=None)
        worst = min(analytics, key=lambda item: item["reliability_index"], default=None)
        return {
            "total_cameras": total,
            "online_count": status["online_count"] or 0,
            "offline_count": status["offline_count"] or 0,
            "unstable_count": status["unstable_count"] or 0,
            "overall_uptime_pct": overall_uptime,
            "total_incidents_30days": incidents or 0,
            "most_reliable_camera": best["name"] if best else None,
            "least_reliable_camera": worst["name"] if worst else None,
        }
    except Exception:
        return {"total_cameras": 0, "online_count": 0, "offline_count": 0, "unstable_count": 0, "overall_uptime_pct": 0, "total_incidents_30days": 0, "most_reliable_camera": None, "least_reliable_camera": None}
