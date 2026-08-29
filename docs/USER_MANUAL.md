# User Manual

## Login

1. Open `http://127.0.0.1:8000`.
2. Enter username and password.
3. Use the dashboard to review camera health.

## Dashboard

The dashboard provides a quick operational summary:

- Total cameras
- Healthy cameras
- Warning cameras
- Offline cameras
- Uptime and health overview
- Infrastructure summary
- AI overview

Use the dashboard for high-level status. Use detailed pages for investigation.

## Registered Cameras

The registered cameras page shows each monitored camera card.

Typical card information:

- Camera name
- Health percentage
- Status
- Latency
- Packet loss
- IP address
- Switch
- RTSP status

Open the card actions to view details, ping a camera, inspect topology, or edit camera information.

## Camera Management

Use Camera Management to add or edit a camera.

Required fields:

- Camera name
- Camera IP
- Location
- Switch name
- Switch IP
- RTSP URL

The system checks health, online/offline state, and latency automatically.

## Network Topology

The topology page shows the relationship between switches and cameras. Use it to identify whether issues are isolated to one camera or shared across a switch/network segment.

## Alerts

The alerts page shows operational incidents with diagnosis, severity, confidence, recommended action, timestamp, and resolution status.

## Notification History

Notification history is read-only. It shows email and Telegram delivery attempts with recipient, status, result, and timestamp.

## Reports

Use reports to download CSV summaries for daily, weekly, or monthly review.

## Global Search

Press:

```text
Ctrl + K
```

Search can find cameras, locations, switches, alerts, and logs.

## Preferences

Preferences include user-facing behavior such as auto refresh interval, theme, compact view, filters, export preferences, and application information.

## Keyboard Shortcuts

- `Ctrl + K`: Open global search
- `Alt + Left Arrow`: Go back to the previous page
- `Alt + 1`: Dashboard
- `Alt + 2`: Registered Cameras
- `Alt + 3`: Camera Management
- `Alt + 4`: Network Topology
- `Alt + 5`: Alerts / Notification History
- `Alt + 6`: Reports / Analytics
- `Alt + 7`: Preferences
- Arrow keys on camera cards: move between camera cards
- Enter or Space on a focused camera card: reveal/select camera actions
