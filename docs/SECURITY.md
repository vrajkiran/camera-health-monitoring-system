# Security Guide

## Authentication

The system includes login and role-based access control.

Default demo login:

```text
Username: admin
Password: Admin@1234
```

This password must be changed before production or client deployment.

## Roles

Common backend roles:

- `ADMINISTRATOR`
- `NETWORK_ENGINEER`

Administrative operations such as user management, camera deletion, settings updates, and monitoring/prediction triggers should remain protected.

## Secret Handling

Never expose these values in frontend code, API responses, screenshots, or documentation:

- SMTP password
- SMTP username if sensitive
- Telegram bot token
- API keys
- JWT secret
- Any production credential

Secrets should be stored in `.env` or backend-only environment variables.

## Safe Settings API

The `/api/settings` response should expose only safe metadata, such as:

- Email configured: true/false
- Telegram configured: true/false
- Notification mode: Automatic
- User preferences

It must not return actual tokens or passwords.

## Deployment Security Checklist

- Change default admin password
- Use a strong JWT secret
- Keep `.env` out of public repositories
- Restrict database file permissions
- Back up SQLite database regularly
- Run the app behind trusted network access controls
- Restrict administrator access to authorized staff
- Review logs for failed login attempts
- Confirm notification recipients are correct before enabling alerts

## Client Handover Note

For client demonstrations, use demo credentials only in a controlled environment. For production, create named administrator accounts and remove unnecessary demo access.
