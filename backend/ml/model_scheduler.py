"""Background scheduler for periodic predictive model retraining."""

import threading
import time

from ml.risk_engine import train_from_database


class ModelTrainingScheduler:
    """Retrain predictive models every 24 hours in a daemon thread."""

    def __init__(self, interval_seconds=86400):
        self.interval_seconds = interval_seconds
        self._started = False

    def start(self):
        if self._started:
            return
        self._started = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            time.sleep(self.interval_seconds)
            try:
                train_from_database()
            except Exception:
                pass
