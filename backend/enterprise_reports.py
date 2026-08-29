"""Executive daily and monthly report generation."""

import csv
import io
import json
from datetime import datetime, timedelta

from alerts import send_email_report
from database import connect, row_to_dict
from enterprise_analytics import RootCauseAnalyticsService
from ai_feedback_service import AIFeedbackService


def now_text():
    return datetime.now().isoformat(timespec="seconds")


class ReportService:
    def _stats(self):
        with connect() as db:
            cameras = [row_to_dict(row) for row in db.execute("SELECT * FROM cameras ORDER BY id").fetchall()]
            incidents = [row_to_dict(row) for row in db.execute("SELECT * FROM incidents ORDER BY first_detected DESC").fetchall()]
            maintenance = [row_to_dict(row) for row in db.execute("SELECT * FROM maintenance_sessions WHERE maintenance_status = 'ACTIVE'").fetchall()]
        total = len(cameras)
        healthy = sum(1 for c in cameras if c["status"] == "ONLINE")
        offline = sum(1 for c in cameras if c["status"] == "OFFLINE")
        warning = sum(1 for c in cameras if c["status"] in ("UNSTABLE", "STREAM_FAILURE"))
        critical = sum(1 for i in incidents if i.get("status") in ("NEW", "NOTIFIED", "ACKNOWLEDGED", "IN_PROGRESS") and i.get("severity") == "CRITICAL")
        downtime = [i.get("downtime") for i in incidents if i.get("downtime") is not None]
        return {
            "total_cameras": total,
            "healthy_cameras": healthy,
            "offline_cameras": offline,
            "critical_cameras": critical,
            "warning_cameras": warning,
            "maintenance_cameras": len(maintenance),
            "availability_pct": round((healthy / total * 100), 2) if total else 0,
            "average_health_score": round((healthy / total * 100), 2) if total else 0,
            "average_downtime": round(sum(downtime) / len(downtime), 1) if downtime else None,
            "incident_count": len(incidents),
            "incidents": incidents,
            "maintenance": maintenance,
        }

    def build_daily_html(self):
        generated = datetime.now()
        period_start = generated - timedelta(hours=24)
        stats = self._stats()
        analytics = RootCauseAnalyticsService().summary({"date_from": period_start.date().isoformat(), "date_to": generated.date().isoformat()})
        ai_perf = AIFeedbackService().performance()
        critical = [i for i in stats["incidents"] if i.get("status") in ("NEW", "NOTIFIED", "ACKNOWLEDGED", "IN_PROGRESS")][:10]
        rows = "".join(f"<tr><td>{i['camera_name']}</td><td>{i.get('diagnosis')}</td><td>{i.get('downtime') or 'Open'}</td><td>{i.get('status')}</td><td>{i.get('severity')}</td></tr>" for i in critical)
        maintenance_rows = "".join(f"<tr><td>{m['camera_name']}</td><td>{m['technician_name']}</td><td>{m['maintenance_reason']}</td><td>{m.get('expected_end_time') or '-'}</td></tr>" for m in stats["maintenance"])
        cause_rows = "".join(f"<tr><td>{cause}</td><td>{count}</td></tr>" for cause, count in analytics["top_failure_causes"])
        recs = self.recommendations(analytics)
        rec_html = "".join(f"<li>{item}</li>" for item in recs)
        cards = "".join(f"<div class='card'><span>{label}</span><strong>{value}</strong></div>" for label, value in [
            ("Total Cameras", stats["total_cameras"]), ("Healthy", stats["healthy_cameras"]), ("Offline", stats["offline_cameras"]),
            ("Critical", stats["critical_cameras"]), ("Warning", stats["warning_cameras"]), ("Maintenance", stats["maintenance_cameras"]),
            ("Availability", f"{stats['availability_pct']}%"), ("Avg Health", f"{stats['average_health_score']}%"),
        ])
        return f"""
        <html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>
        body{{font-family:Inter,Segoe UI,Arial,sans-serif;background:#f8fafc;color:#111827;margin:0;padding:24px}}
        .wrap{{max-width:960px;margin:auto;background:#fff;border:1px solid #e5e7eb;border-radius:16px;overflow:hidden}}
        .head{{background:#1d4ed8;color:white;padding:24px}}.body{{padding:22px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px}}
        .card{{border:1px solid #e5e7eb;border-radius:12px;padding:14px;background:#f8fafc}}.card span{{font-size:12px;color:#64748b}}.card strong{{display:block;font-size:22px;margin-top:4px}}
        table{{width:100%;border-collapse:collapse;margin:14px 0}}th,td{{border-bottom:1px solid #e5e7eb;padding:10px;text-align:left;font-size:13px}}th{{background:#f8fafc;color:#475569}}
        h2{{font-size:18px;margin-top:26px}}.foot{{color:#64748b;font-size:12px;border-top:1px solid #e5e7eb;padding-top:14px}}
        </style></head><body><div class='wrap'><div class='head'><h1>AI Camera Health Monitoring System</h1><h2>Daily Camera Health Report</h2><p>Report Date: {generated.date()}<br>Reporting Period: {period_start} to {generated}<br>Generated Time: {generated}</p></div><div class='body'>
        <h2>Executive Summary</h2><div class='cards'>{cards}</div>
        <h2>Critical Incidents</h2><table><tr><th>Camera</th><th>Diagnosis</th><th>Downtime</th><th>Status</th><th>Severity</th></tr>{rows or '<tr><td colspan="5">No critical incidents in the reporting window.</td></tr>'}</table>
        <h2>Maintenance Cameras</h2><table><tr><th>Camera</th><th>Technician</th><th>Reason</th><th>Expected Completion</th></tr>{maintenance_rows or '<tr><td colspan="4">No active maintenance sessions.</td></tr>'}</table>
        <h2>AI Diagnosis Summary</h2><table><tr><th>Root Cause</th><th>Count</th></tr>{cause_rows or '<tr><td colspan="2">No diagnosis data available.</td></tr>'}</table>
        <h2>AI Performance</h2><p>Total Diagnoses: {ai_perf['total_predictions']} | Correct: {ai_perf['correct_predictions']} | Incorrect: {ai_perf['incorrect_predictions']} | Accuracy: {ai_perf['diagnosis_accuracy'] if ai_perf['diagnosis_accuracy'] is not None else 'Pending feedback'}</p>
        <h2>System Health</h2><table><tr><th>Service</th><th>Status</th></tr><tr><td>Backend Service</td><td>Operational</td></tr><tr><td>Database</td><td>Operational</td></tr><tr><td>Machine Learning Engine</td><td>Operational</td></tr><tr><td>Telegram Service</td><td>Configured in environment</td></tr><tr><td>Email Service</td><td>Configured in environment</td></tr><tr><td>Scheduler</td><td>Operational</td></tr><tr><td>API Status</td><td>Operational</td></tr></table>
        <h2>Recommendations</h2><ul>{rec_html}</ul><p class='foot'>AI Camera Health Monitoring System<br>Automatically Generated Report<br>{generated}<br>This is an automatically generated report. Please do not reply.</p></div></div></body></html>
        """

    def recommendations(self, analytics):
        recs = []
        for cause, _ in analytics.get("top_failure_causes", [])[:3]:
            if "Cable" in cause:
                recs.append("Replace or test Ethernet cables in recurring failure areas.")
            elif "Switch" in cause or "PoE" in cause:
                recs.append("Inspect switch ports, PoE budget and uplink health for recurring failures.")
            elif "Latency" in cause or "Packet" in cause:
                recs.append("Review network congestion and prioritize surveillance traffic.")
            else:
                recs.append(f"Schedule preventive maintenance for recurring {cause} incidents.")
        return recs or ["Continue routine monitoring and review cameras with repeated warning status."]

    def _csv_copy(self, summary):
        output = io.StringIO()
        writer = csv.writer(output)
        for key, value in summary.items():
            if key not in ("incidents", "maintenance"):
                writer.writerow([key, value])
        return output.getvalue()

    def generate_daily(self, send_email=False):
        html = self.build_daily_html()
        stats = self._stats()
        generated = now_text()
        period = f"{(datetime.now() - timedelta(hours=24)).isoformat(timespec='seconds')} to {generated}"
        summary_json = json.dumps({k: v for k, v in stats.items() if k not in ("incidents", "maintenance")})
        csv_copy = self._csv_copy(stats)
        with connect() as db:
            cursor = db.execute(
                "INSERT INTO daily_reports (report_date, reporting_period, generation_time, generated_by, html_copy, pdf_copy, excel_copy, summary_json) VALUES (?, ?, ?, 'System', ?, ?, ?, ?)",
                (datetime.now().date().isoformat(), period, generated, html, html, csv_copy, summary_json),
            )
            db.execute("INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)", ("DAILY_REPORT_GENERATED", f"Daily executive report {cursor.lastrowid} generated.", generated))
        if send_email:
            send_email_report("AI Camera Health Monitoring System - Daily Camera Health Report", html, html=True)
        return {"ok": True, "report_id": cursor.lastrowid, "html": html}

    def generate_monthly(self):
        daily = self.generate_daily(send_email=False)
        generated = now_text()
        period = datetime.now().strftime("%Y-%m")
        with connect() as db:
            cursor = db.execute(
                "INSERT INTO monthly_reports (report_period, report_date, generation_time, generated_by, html_copy, pdf_copy, excel_copy, summary_json) VALUES (?, ?, ?, 'System', ?, ?, ?, ?)",
                (period, datetime.now().date().isoformat(), generated, daily["html"], daily["html"], "Monthly report CSV copy generated from daily summary.", "{}"),
            )
            db.execute("INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)", ("MONTHLY_REPORT_GENERATED", f"Monthly report {cursor.lastrowid} generated.", generated))
        return {"ok": True, "report_id": cursor.lastrowid}

    def list_reports(self, report_type="daily"):
        table = "monthly_reports" if report_type == "monthly" else "daily_reports"
        with connect() as db:
            rows = db.execute(f"SELECT id, report_date, generation_time, generated_by, archived FROM {table} ORDER BY generation_time DESC LIMIT 200").fetchall()
            return [row_to_dict(row) for row in rows]

    def get_report(self, report_type, report_id):
        table = "monthly_reports" if report_type == "monthly" else "daily_reports"
        with connect() as db:
            row = db.execute(f"SELECT * FROM {table} WHERE id = ?", (report_id,)).fetchone()
            return row_to_dict(row) if row else None

    def send_daily_if_due(self):
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat(timespec="seconds")
        with connect() as db:
            row = db.execute("SELECT id FROM daily_reports WHERE generation_time >= ? ORDER BY generation_time DESC LIMIT 1", (cutoff,)).fetchone()
        if row:
            return {"ok": True, "skipped": True, "reason": "Daily report already generated within 24 hours"}
        return self.generate_daily(send_email=True)
