# API Reference

Base URL:

```text
http://127.0.0.1:8000
```

Most endpoints return JSON. Protected write operations require authentication and role permission.

## Health and Platform

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Backend and database health check |
| GET | `/api/config/status` | Email/Telegram configured status without secrets |
| GET | `/api/platform/status` | Platform service status summary |
| GET | `/api/monitoring/status` | Monitoring engine status |
| GET | `/api/dashboard/summary` | Main dashboard summary and diagnosis summary |

## Authentication and Users

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Login and receive session payload |
| POST | `/api/auth/logout` | Logout response |
| GET | `/api/auth/me` | Current authenticated user |
| GET | `/api/users` | List users, administrator only |
| POST | `/api/users` | Create user, administrator only |
| PUT | `/api/users/{id}/password` | Change user password, administrator only |

## Cameras

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/cameras` | List all cameras |
| GET | `/api/cameras/{id}` | Get one camera |
| POST | `/api/cameras` | Create camera, administrator/network engineer |
| PUT | `/api/cameras/{id}` | Update camera, administrator/network engineer |
| DELETE | `/api/cameras/{id}` | Delete camera, administrator only |
| PUT | `/api/cameras/{id}/status` | Update camera status, administrator/network engineer |
| GET | `/api/cameras/stats` | Camera count and health summary |
| GET | `/api/cameras/health-summary` | Health distribution |
| GET | `/api/cameras/latency-stats` | Latency statistics |
| GET | `/api/cameras/{id}/ping-history` | Ping history for one camera |
| GET | `/api/cameras/stream-status` | RTSP/stream status overview |

## Monitoring and Checks

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/monitor/tick` | Trigger one monitoring cycle, administrator/network engineer |
| GET | `/api/switches/stats` | Switch health summary |
| GET | `/api/topology` | Network topology data |

## Alerts, Diagnosis, and Notifications

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/alerts` | Enriched alert list with diagnosis and recommendations |
| PUT | `/api/alerts/{id}/read` | Mark alert as read |
| GET | `/api/diagnosis/history` | Diagnosis history |
| GET | `/api/recommendations` | Central diagnosis recommendation catalog |
| GET | `/api/notifications/history` | Notification delivery history |

Manual notification trigger endpoints are intentionally disabled. Email and Telegram delivery are automatic.

| Method | Endpoint | Status |
|---|---|---|
| POST | `/api/alerts/daily-email-report` | Disabled, returns 404 message |
| POST | `/api/alerts/telegram-network-alert` | Disabled, returns 404 message |

## ML and Analytics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/ml/statistics` | Read-only ML statistics |
| GET | `/api/predictions` | Latest prediction rows |
| GET | `/api/predictions/{camera_id}` | Prediction details for one camera |
| POST | `/api/predictions/run` | Run prediction job, administrator/network engineer |
| GET | `/api/analytics/summary` | Camera analytics summary |
| GET | `/api/analytics/downtime-trend` | Downtime trend data |
| GET | `/api/analytics/system` | System analytics summary |
| GET | `/api/escalations` | Escalation data |

## Reports

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reports/daily` | Daily CSV report |
| GET | `/api/reports/weekly` | Weekly CSV report |
| GET | `/api/reports/monthly` | Monthly CSV report |

PDF export is not part of the current application. Reports are CSV-only.

## Settings and Logs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/settings` | User preferences and safe notification configuration status |
| PUT | `/api/settings` | Update preferences, administrator only |
| GET | `/api/logs` | Application/system logs |
| GET | `/api/user-activity` | User activity history |

## Important Response Notes

- `/api/settings` must not expose SMTP password, Telegram token, API keys, or secret values.
- `/api/ml/statistics` should return backend-derived values only.
- Alerts include diagnosis, confidence, recommended action, severity, timestamp, and resolution status.
