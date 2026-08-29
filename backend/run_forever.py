import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import app


LOG_PATH = Path(__file__).resolve().parent / "backend.log"


def log(message):
    timestamp = datetime.now().isoformat(timespec="seconds")
    LOG_PATH.open("a", encoding="utf-8").write(f"[{timestamp}] {message}\n")


if __name__ == "__main__":
    log("Backend watchdog starting")
    while True:
        try:
            log("Starting backend server on http://127.0.0.1:8000")
            app.main()
        except KeyboardInterrupt:
            log("Backend stopped by keyboard interrupt")
            raise
        except Exception:
            log("Backend crashed:")
            LOG_PATH.open("a", encoding="utf-8").write(traceback.format_exc() + "\n")
            time.sleep(2)
