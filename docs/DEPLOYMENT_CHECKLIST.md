# Deployment Checklist

## Pre-Deployment

- Confirm Python is installed
- Confirm the project runs locally on port 8000
- Confirm database file exists
- Confirm 25 demo cameras are available or replace with production camera inventory
- Change default administrator password
- Configure environment variables
- Confirm `.env` is not shared publicly

## Configuration

Set production values for:

- JWT secret
- Email SMTP host and port
- Email sender
- Email recipients
- Telegram bot token
- Telegram chat ID

Keep credentials backend-only.

## Network Validation

- Confirm backend server can reach camera IP ranges
- Confirm switch IPs are reachable
- Confirm RTSP URLs follow the correct format
- Confirm firewall rules allow required traffic
- Confirm notification services can reach email/Telegram endpoints

## Application Validation

- Login works
- Dashboard loads
- Registered Cameras page shows all expected cameras
- Camera Management can add/edit camera data
- Run Check works
- Auto Refresh updates the dashboard
- Global Search works with `Ctrl + K``r`n- Global back works with the header arrow and `Alt + Left Arrow``r`n- Camera cards support keyboard focus and arrow navigation`r`n- Dark Mode and Default Landing Page preferences apply immediately
- Network Topology displays switch-camera relationships
- Prediction, diagnosis, and recommendation highlights show backend data`r`n- Alerts include diagnosis and recommendations
- Notification History records delivery attempts
- Reports download as CSV

## Backup

Before handover:

```powershell
Copy-Item backend\cc_camera_demo.db backend\cc_camera_demo.handover-backup.db
```

## Client Handover

Provide the client with:

- Application URL
- Login account details for approved users
- Run/start instructions
- Backup process
- Contact/escalation procedure
- This documentation folder

## Post-Deployment

- Monitor logs after first live day
- Verify daily email report delivery
- Verify Telegram incident alerts
- Review unresolved diagnosis records
- Replace demo camera records with actual campus inventory if needed

