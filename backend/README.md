# CC Camera Backend

This backend uses only Python standard-library modules:

- SQLite database: `backend/cc_camera_demo.db`
- Local API server: `http://127.0.0.1:8000`
- Email alerts: Gmail SMTP
- Telegram alerts: Telegram Bot API
- SMS: intentionally not included

## Run

```powershell
python backend\app.py
```

Then open:

```text
http://127.0.0.1:8000
```

## Demo API

- `GET /api/health`
- `GET /api/cameras`
- `GET /api/cameras/stats`
- `GET /api/alerts`
- `GET /api/logs`
- `GET /api/cameras/1/ping-history`
- `PUT /api/alerts/1/read`
- `PUT /api/cameras/1/status` with `{"status":"OFFLINE"}`
- `POST /api/demo/reset`

## Telegram And Email

Edit `.env` in the project root:

- `GMAIL_USER`
- `GMAIL_APP_PASSWORD`
- `ADMIN_EMAIL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Test alert endpoints:

- `POST /api/alerts/test-email`
- `POST /api/alerts/test-telegram`
