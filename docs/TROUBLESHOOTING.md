# Troubleshooting

## Browser Shows "This Site Can't Be Reached"

The backend is not running or port 8000 is unavailable.

Fix:

```powershell
cd "C:\Users\Intel\OneDrive\문서\Projects\camera-health-monitoring-system"
.\run-backend-logged.bat
```

Open:

```text
http://127.0.0.1:8000
```

## Blank White Page

Possible causes:

- Opening `dist/index.html` directly as a file
- Browser cache contains old JavaScript
- Backend is not serving the dashboard

Fix:

- Use `http://127.0.0.1:8000`
- Hard refresh the browser with `Ctrl + F5`
- Restart the backend

## Backend Health Check

Open:

```text
http://127.0.0.1:8000/api/health
```

Expected result includes:

```json
{"ok": true}
```

## Login Fails

Check:

- Correct username and password
- Backend is running
- Database exists at `backend/cc_camera_demo.db`
- Default account has not been changed

## Camera Count Looks Wrong

The demo database should contain 25 bundled cameras. If fewer appear, restart the backend so `ensure_demo_cameras` can backfill missing demo records.

## ML Section Shows Dashes

The frontend only displays backend ML values. If no prediction data exists, run prediction from the authorized control or check:

```text
/api/ml/statistics
/api/predictions
```

## Global Search Does Not Open

Use:

```text
Ctrl + K
```

If it still fails, hard refresh the browser and confirm the backend is serving the latest `dist/index.html`.

## Email or Telegram Not Sending

Check:

- `.env` contains the required values
- Recipient/chat ID is correct
- Network access is available
- Notification service is configured
- Notification history records the delivery result

Do not debug by printing secrets to the frontend or logs.

## CSV Report Does Not Download

Check report endpoints:

```text
/api/reports/daily
/api/reports/weekly
/api/reports/monthly
```

PDF export is not supported in the current version.
