# Project Overview

## Purpose

The UCEK-JNTUK Camera Health Monitoring System is an enterprise-style monitoring platform for campus CCTV infrastructure. It helps operations teams understand whether cameras and associated network components are reachable, healthy, unstable, or offline.

The platform has been extended from simple camera failure detection into an intelligent diagnosis and recommendation system. It now identifies probable root causes, records diagnosis history, tracks notifications, and exposes ML prediction information without changing the existing application flow.

## Intended Users

- Campus surveillance administrators
- Network engineers
- IT operations teams
- Maintenance teams
- Management users who need camera availability summaries

## Main Modules

- Dashboard summary
- Registered camera monitoring
- Camera management
- Network topology
- Alerts
- Notification history
- Reports and analytics
- ML prediction overview
- Diagnosis history
- Activity log
- Preferences

## Monitoring Scope

The system tracks:

- Camera online/offline state
- Camera health percentage
- Latency
- Packet loss
- Heartbeat/check timestamp
- RTSP service status
- Associated switch and switch IP
- Switch-level availability
- Diagnosis and recommended action
- Notification delivery history

## What the System Does Not Do

- It does not replace a VMS/NVR.
- It does not stream or record live CCTV footage.
- It does not expose SMTP passwords, Telegram tokens, or API keys through the frontend.
- It does not generate fake ML statistics. ML display values are based on backend data.

## Demo Data

The backend includes 25 demo cameras so the platform can be presented and tested immediately. Demo data is stored in SQLite and can be reset or extended.
