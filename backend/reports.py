"""CSV report generation for UCEK-JNTUK camera health analytics."""

import csv
from datetime import datetime
from io import StringIO

from analytics import get_camera_analytics


def generate_csv_report(period_days):
    """Generate a CSV camera health report as a string."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([f"UCEK-JNTUK Camera Health Report - Last {period_days} Days - {datetime.now().strftime('%Y-%m-%d')}"])
    writer.writerow([])
    writer.writerow(["Camera Name", "Location", "Status", "Uptime %", "Avg Latency (ms)", "Incidents", "MTTR (min)", "Reliability Index"])
    for item in get_camera_analytics():
        writer.writerow([
            item["name"],
            item["location"],
            item["status"],
            item["uptime_pct"],
            "" if item["avg_latency"] is None else item["avg_latency"],
            item["incident_count"],
            "" if item["mttr_minutes"] is None else item["mttr_minutes"],
            item["reliability_index"],
        ])
    return output.getvalue()
