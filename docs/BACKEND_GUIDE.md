# Backend Guide

## Location

```text
backend/
```

Main entry point:

```text
backend/app.py
```

## Backend Responsibilities

The backend provides:

- Static frontend serving
- REST API routing
- Authentication and role checks
- Camera CRUD
- Monitoring execution
- Camera/switch statistics
- Diagnosis and recommendations
- Notification history
- ML statistics and predictions
- CSV reports
- User activity logs
- Safe settings management

## Main Files

| File | Responsibility |
|---|---|
| `app.py` | HTTP server, routes, API handlers, static file serving |
| `database.py` | SQLite schema, connection helper, demo data |
| `auth.py` | Login, password hashing, token/session handling, roles |
| `diagnosis_engine.py` | Root cause diagnosis and reusable recommendations |
| `analytics.py` | Analytics summaries and downtime trends |
| `reports.py` | CSV report generation |
| `topology.py` | Network topology data generation |
| `config.py` | Environment-backed configuration |
| `monitoring/monitor_scheduler.py` | Periodic monitoring, status transitions, automatic notifications |
| `ml/` | Machine learning/prediction logic |
| `alerts/` | Email and Telegram delivery helpers |
| `websocket/` | WebSocket support, if enabled |

## Server Behavior

The backend listens on port 8000 by default and serves:

- `/` as the dashboard page
- `/api/...` as JSON APIs
- static files from `dist/`

## Monitoring Behavior

Monitoring checks camera reachability, latency, stream status, and switch association. When a meaningful status transition occurs, the backend records events, creates diagnosis history, updates downtime information, and triggers automatic notifications when configured.

## Notification Behavior

Manual notification triggers are disabled. Notifications are generated automatically by backend logic.

Telegram alerts are used for operational incidents such as:

- Camera offline
- Camera failure
- Switch failure
- Critical network failure

Email is intended for daily health summaries.

## Settings Safety

The settings API returns safe configuration state only. It must not expose credentials or tokens.

Examples of safe values:

- Email configured: true/false
- Telegram configured: true/false
- Notification mode: Automatic

Examples of unsafe values that must not be returned:

- SMTP password
- Telegram bot token
- API keys
- JWT secret

## Logging

The backend stores operational logs in database tables and writes runtime information to backend log files. Logs should support incident review, audit activity, and maintenance decisions.
