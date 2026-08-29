from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_env():
    values = {}
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


ENV = load_env()
DATABASE_PATH = (BASE_DIR / ENV.get("DATABASE_PATH", "backend/cc_camera_demo.db")).resolve()

GMAIL_USER = ENV.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = ENV.get("GMAIL_APP_PASSWORD", "")
ADMIN_EMAIL = ENV.get("ADMIN_EMAIL", "")

TELEGRAM_BOT_TOKEN = ENV.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = ENV.get("TELEGRAM_CHAT_ID", "")
JWT_SECRET = ENV.get("JWT_SECRET", "ucek-jntuk-cctv-secret-2024")
