"""Enterprise root-cause analytics service."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta

from database import connect, row_to_dict

CAUSE_MAP = {
    "Power Failure": "Power Failure",
    "PoE Failure": "PoE Failure",
    "Switch Port Failure": "Switch Failure",
    "Ethernet Cable Failure": "Ethernet Cable Failure",
    "High Packet Loss": "High Packet Loss",
    "High Latency": "High Latency",
    "RTSP Service Failure": "RTSP Failure",
    "Authentication Failure": "Authentication Failure",
    "Camera Hardware Failure": "Camera Hardware Failure",
    "Camera Firmware Failure": "Firmware Failure",
}


def _cause(value):
    return CAUSE_MAP.get(value or "", "Unknown Cause")


class RootCauseAnalyticsService:
    def summary(self, filters=None):
        filters = filters or {}
        since = filters.get("date_from") or (datetime.now() - timedelta(days=365)).date().isoformat()
        until = filters.get("date_to") or datetime.now().date().isoformat()
        with connect() as db:
            rows = [row_to_dict(row) for row in db.execute(
                """
                SELECT i.*, c.location, c.switch_id, c.latency_ms
                FROM incidents i LEFT JOIN cameras c ON c.id = i.camera_id
                WHERE substr(i.first_detected, 1, 10) BETWEEN ? AND ?
                ORDER BY i.first_detected DESC
                """,
                (since, until),
            ).fetchall()]
        if filters.get("building"):
            rows = [row for row in rows if row.get("location") == filters["building"]]
        if filters.get("camera_id"):
            rows = [row for row in rows if str(row.get("camera_id")) == str(filters["camera_id"])]
        if filters.get("severity"):
            rows = [row for row in rows if row.get("severity") == filters["severity"]]
        causes = Counter(_cause(row.get("diagnosis")) for row in rows)
        cameras = Counter(row.get("camera_name") for row in rows if row.get("camera_name"))
        switches = Counter(row.get("switch_id") for row in rows if row.get("switch_id"))
        buildings = Counter(row.get("location") for row in rows if row.get("location"))
        severities = Counter(row.get("severity") for row in rows if row.get("severity"))
        downtime = [row.get("downtime") for row in rows if row.get("downtime") is not None]
        health_scores = []
        weekly = defaultdict(int)
        monthly = defaultdict(int)
        for row in rows:
            if row.get("latency_ms") is None:
                health_scores.append(0)
            elif row.get("latency_ms") >= 150:
                health_scores.append(65)
            else:
                health_scores.append(100)
            dt = datetime.fromisoformat(row["first_detected"])
            weekly[f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"] += 1
            monthly[dt.strftime("%Y-%m")] += 1
        return {
            "total_incidents": len(rows),
            "top_failure_causes": causes.most_common(10),
            "most_problematic_cameras": cameras.most_common(10),
            "most_problematic_switches": switches.most_common(10),
            "most_affected_buildings": buildings.most_common(10),
            "most_affected_floors": [],
            "most_frequent_incident_types": severities.most_common(10),
            "average_downtime": round(sum(downtime) / len(downtime), 1) if downtime else None,
            "average_resolution_time": round(sum(downtime) / len(downtime), 1) if downtime else None,
            "average_health_score": round(sum(health_scores) / len(health_scores), 1) if health_scores else None,
            "weekly_incident_trend": [{"period": k, "count": v} for k, v in sorted(weekly.items())],
            "monthly_incident_trend": [{"period": k, "count": v} for k, v in sorted(monthly.items())],
            "pie_chart": [{"label": k, "value": v} for k, v in causes.most_common()],
            "bar_chart": [{"label": k, "value": v} for k, v in cameras.most_common(10)],
        }

    def refresh_statistics(self):
        summary = self.summary()
        now = datetime.now().isoformat(timespec="seconds")
        with connect() as db:
            db.execute("DELETE FROM root_cause_statistics")
            for cause, count in summary["top_failure_causes"]:
                db.execute(
                    "INSERT INTO root_cause_statistics (cause, incident_count, avg_downtime_minutes, last_updated) VALUES (?, ?, ?, ?)",
                    (cause, count, summary.get("average_downtime"), now),
                )
            db.execute("INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)", ("ANALYTICS_UPDATED", "Root cause analytics statistics refreshed.", now))
        return summary
