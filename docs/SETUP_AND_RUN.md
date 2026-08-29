# Setup and Run Guide

## Requirements

- Windows 10 or Windows 11
- Python 3.x
- Modern browser such as Chrome or Edge
- Node.js is optional and only needed for frontend build/static tooling

## Main Application URL

```text
http://127.0.0.1:8000
```

The backend serves both the API and the frontend.

## Recommended Local Run

Open PowerShell in the project folder:

```powershell
cd "C:\Users\Intel\OneDrive\문서\Projects\cc-camera-frontend-only"
```

Start the application:

```powershell
.\run-backend-logged.bat
```

Then open:

```text
http://127.0.0.1:8000
```

## Alternative Run Command

```powershell
.\start-backend.bat
```

Or directly:

```powershell
python backend\app.py
```

## Login

Demo administrator credentials:

```text
Username: admin
Password: Admin@1234
```

Change this password before production use.

## Frontend Runtime

The frontend is already built as `dist/index.html` and is served by the Python backend. The removed React/Vite development layer is not required to run the application.

The optional Node static server remains only for static file preview:

```powershell
npm run serve
```

For normal use, always open the backend URL on port 8000.

## Environment Configuration

Sensitive values are stored in `.env` and backend configuration. Do not hard-code secrets into frontend files.

Common configuration items:

```text
JWT_SECRET
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
EMAIL_FROM
EMAIL_RECIPIENTS
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Never publish real tokens or passwords in screenshots, documentation, GitHub, or client handover files.

## Verifying the Backend

Open these URLs after starting the app:

```text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/api/cameras/stats
http://127.0.0.1:8000/api/ml/statistics
```

A working health endpoint returns JSON with `ok: true`.

