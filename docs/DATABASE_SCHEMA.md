# Database Schema

Database file:

```text
backend/cc_camera_demo.db
```

Database engine:

```text
SQLite
```

Schema and demo data are managed in:

```text
backend/database.py
```

## Core Tables

### cameras

Stores registered camera inventory and latest health state.

Important fields:

- `id`
- `name`
- `location`
- `ip_address`
- `switch_name`
- `switch_ip`
- `rtsp_url`
- `status`
- `latency_ms`
- `health_note`
- `health_score`
- `last_checked`

### alerts

Stores operational alerts.

Important fields:

- `id`
- `camera_id`
- `camera_name`
- `type`
- `message`
- `created_at`
- `is_read`

Alerts are enriched at API level with diagnosis, confidence, severity, recommended action, and resolution status.

### downtime_logs

Stores downtime incidents and recovery information.

Important fields:

- `id`
- `camera_id`
- `started_at`
- `ended_at`
- `duration_minutes`
- `root_cause`

### ping_history

Stores latency and reachability samples.

Important fields:

- `id`
- `camera_id`
- `latency_ms`
- `packet_loss`
- `checked_at`

### settings

Stores user-facing preferences and notification configuration metadata.

Sensitive values must remain backend-only and must not be exposed through the settings API.

### users

Stores application users and roles.

Important fields:

- `id`
- `username`
- `password_hash`
- `role`
- `created_at`

### user_activity

Stores user actions for audit and operational visibility.

### predictions

Stores ML prediction output for camera risk and possible failure windows.

### escalations

Stores escalation records for operational follow-up.

## Intelligent Monitoring Tables

### diagnosis_history

Stores root-cause diagnosis records.

Important fields:

- `id`
- `camera_id`
- `camera_name`
- `diagnosis`
- `confidence`
- `severity`
- `recommendation`
- `resolution_status`
- `created_at`
- `resolved_at`

### notification_history

Stores every automatic notification attempt.

Important fields:

- `id`
- `notification_type`
- `recipient`
- `status`
- `delivery_result`
- `created_at`

## Demo Data

The application includes 25 demo cameras in `DEMO_CAMERAS`. The helper `ensure_demo_cameras(db)` backfills missing demo cameras without deleting user-created records.

## Backup Recommendation

Before production deployment or major schema changes, copy the SQLite database:

```powershell
Copy-Item backend\cc_camera_demo.db backend\cc_camera_demo.backup.db
```
