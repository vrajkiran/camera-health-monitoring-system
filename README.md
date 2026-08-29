# UCEK-JNTUK Camera Health Monitoring System

A campus surveillance health monitoring platform for UCEK-JNTUK. The system monitors registered CCTV cameras, network reachability, switch association, RTSP availability, latency, packet loss, alerts, diagnosis history, notification history, ML risk predictions, and CSV reports.

This application is focused on camera health monitoring and operational decision support. It is not a live CCTV viewing system.

## Quick Start

1. Open the project folder:

```powershell
cd "C:\Users\Intel\OneDrive\문서\Projects\camera-health-monitoring-system"
```

2. Start the backend and frontend together:

```powershell
.\run-backend-logged.bat
```

3. Open the application:

```text
http://127.0.0.1:8000
```

4. Login with the demo administrator account:

```text
Username: admin
Password: Admin@1234
```

Change the default password before using the system in a real environment.

## What Runs on Port 8000

The Python backend serves both:

- The frontend dashboard from `dist/index.html`
- The REST API under `/api/...`

This means `http://127.0.0.1:8000` is the main application URL.

## Documentation

- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [Setup and Run Guide](docs/SETUP_AND_RUN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Frontend Guide](docs/FRONTEND_GUIDE.md)
- [Backend Guide](docs/BACKEND_GUIDE.md)
- [Diagnosis and ML](docs/DIAGNOSIS_AND_ML.md)
- [Notifications and Reports](docs/NOTIFICATIONS_AND_REPORTS.md)
- [Security Guide](docs/SECURITY.md)
- [User Manual](docs/USER_MANUAL.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md)

## Current Key Capabilities

- 25 demo camera records for campus-style testing
- Camera registration and edit workflow
- Online, offline, warning, latency, and RTSP status tracking
- Switch-aware monitoring and topology view
- Diagnosis engine with professional root-cause categories
- Central recommendation engine
- ML statistics, prediction focus, diagnosis highlights, and recommendation visibility
- Automatic notification history
- CSV reports`r`n- Keyboard navigation with global back, Ctrl+K search, and camera-card arrow navigation`r`n- Preferences with Auto Refresh, Dark Mode, Compact View, and Default Landing Page
- Role-based authentication
- Secret-safe settings API

## Project Structure

```text
camera-health-monitoring-system/
  backend/                 Python backend, database, monitoring, ML, alerts
  dist/index.html          Production frontend, keyboard controls, dark mode, AI highlights
  docs/                    Project documentation
  .env                     Local environment configuration, not for sharing
  run-backend-logged.bat   Recommended local launcher
  start-backend.bat        Simple backend launcher
  package.json             Optional frontend/static tooling
```

