# Frontend Guide

## Location

Production frontend:

```text
dist/index.html
```

The backend serves this file at:

```text
http://127.0.0.1:8000
```

The unused React/Vite development layer has been removed. The current served interface is the production dashboard in `dist/index.html`.

## Design Direction

The UI is designed as a premium light enterprise monitoring platform.

Visual standards:

- Background: `#F8FAFC`
- Cards: white
- Primary: blue
- Healthy: green
- Warning: orange
- Offline: red
- Font: Inter
- Icons: Lucide-style visual language
- Rounded cards and controls
- Soft shadows and generous spacing

## Main Navigation

The sidebar is organized around operational workflows:

- Dashboard
- Monitoring
  - Registered Cameras
  - Camera Management
  - Network Topology
- Operations
  - Alerts
  - Notification History
- Insights
  - Reports
  - Analytics
- Administration
  - Activity Log
- Preferences

Developer-only indicators must not be shown to client users.

## Top Navigation

Top navigation includes:

- Global search
- Notifications
- Auto refresh status
- Platform status labels
- Last synchronization
- User profile

Client-facing status labels should use professional language such as:

- Monitoring Active
- Camera Monitoring
- Notification Service
- Last Synchronization

Avoid labels such as `Backend Connected`, `API Running`, or `WebSocket Connected` in the client UI.

## Dashboard

The dashboard should focus on high-value monitoring information:

- Total Cameras
- Healthy
- Warning
- Offline
- Average Uptime
- Camera Health Overview
- Health Trend
- Infrastructure Summary
- AI Overview

The dashboard should not become a dumping area for every module. Detailed data belongs in its dedicated page.

## Registered Cameras

Camera cards display:

- Health ring
- Health percentage
- Heartbeat/last check
- Monitoring status
- Latency
- Packet loss
- IP address
- Switch
- RTSP status

Camera actions should be available through the card curtain reveal interaction:

- View Details
- Alert History
- Ping Camera
- Network Topology
- Edit Camera
- Last Alert
- Notification Status

## Camera Management

Camera management allows add/edit of:

- Camera name
- Camera IP
- Location
- Switch name
- Switch IP
- RTSP URL

Health, online/offline status, and latency should be checked by the system instead of manually entered by the user.

## Global Search

Global search is available with:

```text
Ctrl + K
```

Search groups:

- Cameras
- Buildings/locations
- Switches
- Alerts
- Logs

Search results should take the user to the relevant page or highlighted entity.

## Auto Refresh

Supported intervals:

- 30 seconds
- 1 minute
- 5 minutes
- 10 minutes

Auto refresh should update data without reloading the page and should display the last updated time.

## Preferences

Preferences should include only user-facing options:

- Auto Refresh
- Refresh Interval
- Theme
- Compact View
- Default Filters
- Export Preferences
- Application Information

Do not show SMTP, Telegram token, API key, or developer configuration fields in the frontend.

## Keyboard Control

The application supports keyboard-first operation:

- `Ctrl + K` opens global search.
- `Esc` closes global search.
- `Alt + Left Arrow` activates the global back action.
- `Alt + 1` opens Dashboard.
- `Alt + 2` opens Registered Cameras.
- `Alt + 3` opens Camera Management.
- `Alt + 4` opens Network Topology.
- `Alt + 5` opens Alerts / Notification History.
- `Alt + 6` opens Reports / Analytics.
- `Alt + 7` opens Preferences.
- Camera cards can receive focus; arrow keys move between cards and Enter/Space reveal/select the card actions.

## Intelligence Highlighting

The dashboard now highlights the core project value directly in the AI Overview area:

- Prediction Focus
- Latest Diagnosis
- Diagnosis Confidence and Severity
- Recommendation

These values are loaded from backend prediction, diagnosis, and recommendation APIs.
