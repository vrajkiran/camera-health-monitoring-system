# Notifications and Reports

## Notification Policy

The application uses automatic notifications. Manual notification send buttons and manual notification API triggers are not part of the current client-ready workflow.

## Telegram Alerts

Telegram is intended for immediate operational alerts.

Automatic Telegram alerts are sent for:

- Camera Offline
- Camera Failure
- Switch Failure
- Critical Network Failure

Switch-aware behavior is important: if an entire switch is down, the system should alert on the switch-level incident instead of sending a separate alert for every camera connected to that switch.

## Email Reports

Email is intended for daily summary reporting every 24 hours.

The daily email health report should include:

- Camera Summary
- Health Statistics
- Failure Summary
- Diagnosis Summary
- Switch Summary
- Downtime
- Recommendations

The report should focus on cameras that failed during the day and cameras that remain unresolved at report time.

## Notification History

Every notification attempt is stored in `notification_history`.

Stored fields include:

- Notification type
- Recipient
- Status
- Delivery result
- Timestamp

Notification history is available at:

```text
/api/notifications/history
```

## Alerts

Alerts should include:

- Camera name
- Severity
- Diagnosis
- Confidence
- Recommended action
- Timestamp
- Resolution status

Endpoint:

```text
/api/alerts
```

## Reports

Reports are CSV-only.

Available endpoints:

```text
/api/reports/daily
/api/reports/weekly
/api/reports/monthly
```

PDF reporting has been removed from the current scope.

## Configuration

Email and Telegram credentials must be configured through backend environment variables or backend-only configuration. They must not be displayed in the frontend or returned by public API responses.
