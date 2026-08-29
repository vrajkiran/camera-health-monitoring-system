"""Background scheduler for escalation advancement and periodic risk predictions."""

import threading
import time

from escalation_engine import EscalationEngine
from incidents import IncidentService
from enterprise_reports import ReportService
from maintenance_service import MaintenanceService
from ml.risk_engine import run_all_predictions


class AlertScheduler:
    """Run escalation checks every minute and prediction sweeps every six hours."""

    def __init__(self, interval_seconds=60, prediction_interval_seconds=21600):
        self.interval_seconds = interval_seconds
        self.prediction_interval_seconds = prediction_interval_seconds
        self._started = False
        self._engine = EscalationEngine()
        self._incident_service = IncidentService()
        self._report_service = ReportService()
        self._maintenance_service = MaintenanceService()

    def start(self):
        if self._started:
            return
        self._started = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        last_prediction = 0
        while True:
            try:
                self._incident_service.send_due_reminders()
                self._incident_service.poll_telegram_acknowledgements()
                self._maintenance_service.expire_due_sessions()
                self._report_service.send_daily_if_due()
                now = time.time()
                if now - last_prediction >= self.prediction_interval_seconds:
                    run_all_predictions()
                    last_prediction = now
            except Exception:
                pass
            time.sleep(self.interval_seconds)


