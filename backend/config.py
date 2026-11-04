import secrets
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

# Sentinel values that are considered insecure — never valid JWT secrets.
_INSECURE_SENTINEL_SECRETS = {
    "ucek-jntuk-cctv-secret-2024",
    "change-this-to-a-strong-random-secret",
}


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


def _as_bool(value, default=False):
    if value is None or value == "":
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


ENV = load_env()
_ENV_FILE_EXISTS = (BASE_DIR / ".env").exists()
DATABASE_PATH = (BASE_DIR / ENV.get("DATABASE_PATH", "backend/cc_camera_demo.db")).resolve()

GMAIL_USER = ENV.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = ENV.get("GMAIL_APP_PASSWORD", "")
ADMIN_EMAIL = ENV.get("ADMIN_EMAIL", "")

TELEGRAM_BOT_TOKEN = ENV.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = ENV.get("TELEGRAM_CHAT_ID", "")

# JWT_SECRET must be explicitly set in .env to a strong random value.
# Never falls back to a hardcoded constant — the empty string is intentional
# so that jwt_secret_is_insecure() correctly flags a missing/unset secret.
JWT_SECRET = str(ENV.get("JWT_SECRET") or "")

DEMO_MODE = _as_bool(ENV.get("DEMO_MODE"), default=not _ENV_FILE_EXISTS)

# Allowed CORS origins for browser security. Configurable via .env ALLOWED_ORIGINS.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in ENV.get(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:3010,http://localhost:3010,http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]


def jwt_secret_is_insecure():
    secret = JWT_SECRET.strip()
    return (not secret) or secret in _INSECURE_SENTINEL_SECRETS


def validate_runtime_secrets():
    """Refuse a non-demo start when the JWT signing secret is missing or still a known-weak value."""
    if not jwt_secret_is_insecure():
        return
    message = (
        "JWT_SECRET is missing or still a known-insecure value. "
        "Generate a strong secret (e.g. `python -c \"import secrets; print(secrets.token_hex(32))\"`) "
        "and set JWT_SECRET in your .env file before running without DEMO_MODE."
    )
    if DEMO_MODE:
        print("WARNING: " + message + " DEMO_MODE=true allows local startup.")
        return
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(1)


def generate_secret_hint():
    """Print a ready-to-use strong JWT secret for first-time setup."""
    print("Suggested JWT_SECRET for your .env:")
    print(f"  JWT_SECRET={secrets.token_hex(32)}")
