"""Generate DOCX and PDF project guide for UCEK-JNTUK Camera Health Monitor."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUTPUT_DIR = Path(__file__).resolve().parent
DOCX_PATH = OUTPUT_DIR / "UCEK-JNTUK_Project_Complete_Guide.docx"
PDF_PATH = OUTPUT_DIR / "UCEK-JNTUK_Project_Complete_Guide.pdf"


def set_cell_shading(cell, color: str) -> None:
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color)
    cell._tc.get_or_add_tcPr().append(shading)


def add_title_page(doc: Document) -> None:
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("UCEK-JNTUK Camera Health\nMonitoring System")
    run.bold = True
    run.font.size = Pt(28)
    run.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("Complete Project Guide")
    r.font.size = Pt(18)
    r.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    doc.add_paragraph()
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(
        f"For Presentations · Interviews · Viva · Client Demos · Documentation\n"
        f"Generated: {datetime.now().strftime('%d %B %Y')}\n"
        f"Developer: Raj"
    ).font.size = Pt(11)

    doc.add_page_break()


def h1(doc: Document, text: str) -> None:
    doc.add_heading(text, level=1)


def h2(doc: Document, text: str) -> None:
    doc.add_heading(text, level=2)


def h3(doc: Document, text: str) -> None:
    doc.add_heading(text, level=3)


def p(doc: Document, text: str) -> None:
    doc.add_paragraph(text)


def bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def diagram(doc: Document, text: str) -> None:
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(8)
    para.paragraph_format.left_indent = Inches(0.2)
    para.paragraph_format.space_before = Pt(6)
    para.paragraph_format.space_after = Pt(6)


def table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    hdr = t.rows[0].cells
    for i, header in enumerate(headers):
        hdr[i].text = header
        set_cell_shading(hdr[i], "DBEAFE")
        for run in hdr[i].paragraphs[0].runs:
            run.bold = True
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = value
    doc.add_paragraph()


def build_document() -> Document:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    add_title_page(doc)

    # ── 1. PROJECT OVERVIEW ──
    h1(doc, "1. Project Overview")
    h2(doc, "What problem does this application solve?")
    p(doc, "Campus surveillance teams operate dozens or hundreds of CCTV cameras across buildings, switches, and network segments. When a camera goes offline, teams often discover it only after an incident. This system proactively monitors every registered camera, detects failures early, diagnoses probable root causes, recommends actions, and notifies operators automatically via email and Telegram.")
    h2(doc, "Main Objective")
    p(doc, "Provide a local-first, enterprise-style monitoring dashboard that answers: Which cameras are healthy? Why did a camera fail? What action should maintenance take? Which cameras are at highest risk of failing soon?")
    h2(doc, "Real-World Use Case")
    p(doc, "UCEK-JNTUK campus runs 25+ CCTV cameras across gates, libraries, labs, parking, and admin blocks. When Admin Office CAM-04 goes offline, the system detects it within 30 seconds, diagnoses PoE/Power Failure with confidence %, creates an incident, sends Telegram alert, logs downtime, and shows it on the topology map.")
    h2(doc, "Target Users")
    table(doc, ["User", "Role", "Responsibility"], [
        ["Campus Admin", "ADMINISTRATOR", "Full control, users, settings"],
        ["Network Engineer", "NETWORK_ENGINEER", "Add/edit cameras, maintenance"],
        ["IT Operations", "OPERATOR", "Monitor alerts, acknowledge incidents"],
        ["Management", "VIEWER", "Read-only dashboard and reports"],
    ])
    h2(doc, "Key Features")
    bullets(doc, [
        "Dashboard with health summary and AI overview",
        "Camera monitoring: ping, latency, packet loss, RTSP status",
        "Switch-aware network topology visualization",
        "Rule-based diagnosis engine (12 root-cause categories)",
        "ML risk predictions (Random Forest + Isolation Forest)",
        "Automatic Telegram and Gmail notifications",
        "Incident lifecycle management with escalation",
        "Maintenance mode (alert suppression)",
        "CSV reports (daily, weekly, monthly)",
        "Root cause analytics and AI performance tracking",
        "JWT authentication with role-based access control",
        "WebSocket real-time updates and keyboard-first UX",
    ])
    h2(doc, "What It Does NOT Do")
    bullets(doc, ["Does not stream or record live CCTV video (not a VMS/NVR)", "Does not replace camera vendor management software", "Does not expose SMTP/Telegram secrets to the frontend"])

    # ── 2. SYSTEM ARCHITECTURE ──
    h1(doc, "2. System Architecture")
    h2(doc, "High-Level Architecture Diagram")
    diagram(doc, """
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (Client)                          │
│                   dist/index.html (Vanilla JS)                   │
└────────────┬──────────────────────────────┬─────────────────────┘
             │ REST /api/*                   │ WebSocket ws://8001
             ▼                               ▼
┌────────────────────────────┐   ┌──────────────────────────────┐
│   Python HTTP Server :8000  │   │   WebSocket Server :8001      │
│         backend/app.py      │   │   websocket/websocket_server  │
└────────────┬───────────────┘   └──────────────────────────────┘
             │
    ┌────────┼────────┬──────────┬──────────┬──────────┐
    ▼        ▼        ▼          ▼          ▼          ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐ ┌──────┐ ┌──────────┐
│ Auth │ │Monitor│ │Diag  │ │   ML    │ │Alerts│ │ SQLite   │
│.py   │ │Sched  │ │Engine│ │ Engine  │ │.py   │ │   DB     │
└──────┘ └──────┘ └──────┘ └─────────┘ └──┬───┘ └──────────┘
                                           │
                              ┌────────────┴────────────┐
                              ▼                         ▼
                        Gmail SMTP              Telegram Bot API
                              ▲                         ▲
                              └──── Campus Cameras ─────┘
                                   (ICMP Ping + RTSP)
""")
    h2(doc, "Runtime Components")
    table(doc, ["Component", "Location", "Port", "Responsibility"], [
        ["Frontend", "dist/index.html", "—", "Dashboard UI, routing, charts"],
        ["Backend API", "backend/app.py", "8000", "HTTP routing, auth, static serve"],
        ["WebSocket", "backend/websocket/", "8001", "Real-time event push"],
        ["Database", "backend/cc_camera_demo.db", "—", "SQLite persistence"],
        ["Monitor", "monitoring/monitor_scheduler.py", "—", "30s health checks"],
        ["ML", "backend/ml/", "—", "Risk prediction engine"],
    ])
    h2(doc, "Complete Data Flow")
    diagram(doc, """
User → Browser → POST /api/auth/login → auth.py → SQLite (users)
     → JWT token → GET /api/cameras/stats → app.py → SQLite → JSON → Dashboard

Background (every 30s):
MonitorScheduler → Ping + RTSP → Health Classifier → Update cameras table
  → Status changed? → Diagnosis Engine → Incident Service → Telegram/Email
  → WebSocket dispatch → Browser live update
""")

    # ── 3. SYSTEM DESIGN ──
    h1(doc, "3. System Design")
    h2(doc, "Architecture Pattern: Layered Architecture")
    diagram(doc, """
┌─────────────────────────────────────┐
│  Presentation Layer (dist/index.html)│
├─────────────────────────────────────┤
│  API Layer (app.py HTTP routes)      │
├─────────────────────────────────────┤
│  Business Logic (diagnosis, ML, etc.)│
├─────────────────────────────────────┤
│  Data Access Layer (database.py)     │
├─────────────────────────────────────┤
│  SQLite Database                     │
└─────────────────────────────────────┘
""")
    h2(doc, "Why This Architecture?")
    bullets(doc, ["Simplicity: one Python process serves everything", "Portability: runs on any Windows machine with Python", "No DevOps: no Docker/Kubernetes needed", "Demo-friendly: works immediately with 25 seeded cameras"])
    h2(doc, "Advantages vs Limitations")
    table(doc, ["Advantages", "Limitations"], [
        ["Zero pip dependencies", "Single-threaded SQLite at scale"],
        ["Fast local response (<50ms API)", "Monolithic frontend (one HTML file)"],
        ["Single backup file (SQLite)", "Localhost binding only"],
        ["Easy to present in viva", "Demo IPs use simulated ping"],
    ])

    # ── 4. FOLDER STRUCTURE ──
    h1(doc, "4. Folder Structure")
    diagram(doc, """
cc-camera-frontend-only/
├── backend/              Python backend (API, DB, ML, monitoring)
│   ├── app.py            HTTP server + all routes
│   ├── auth.py           JWT + password hashing
│   ├── database.py       SQLite schema + demo data
│   ├── diagnosis_engine.py
│   ├── monitoring/       Ping, RTSP, scheduler
│   ├── ml/               Feature extraction, training, prediction
│   ├── websocket/        Real-time events
│   ├── alerts/           Email/Telegram + escalation
│   └── incidents.py      Incident lifecycle
├── dist/index.html       Production frontend (active)
├── docs/                 13+ documentation files
├── .env                  Secrets (JWT, Gmail, Telegram)
└── run-backend-logged.bat  Recommended launcher
""")

    # ── 5. MODULE BREAKDOWN ──
    h1(doc, "5. Module Breakdown")
    table(doc, ["Module", "File(s)", "Purpose", "Key Output"], [
        ["Frontend SPA", "dist/index.html", "Dashboard UI", "Rendered pages, charts"],
        ["HTTP API", "backend/app.py", "Route all requests", "JSON, CSV, HTML"],
        ["Authentication", "backend/auth.py", "Login + RBAC", "JWT tokens"],
        ["Database", "backend/database.py", "Persistence", "20+ SQLite tables"],
        ["Monitor Scheduler", "monitoring/monitor_scheduler.py", "30s health checks", "Status updates, WS events"],
        ["Health Classifier", "monitoring/health_classifier.py", "Combine signals", "ONLINE/OFFLINE/UNSTABLE/STREAM_FAILURE"],
        ["Diagnosis Engine", "diagnosis_engine.py", "Root cause analysis", "Diagnosis + confidence + severity"],
        ["Incident Service", "incidents.py", "Incident lifecycle", "Telegram alerts, reminders"],
        ["ML Risk Engine", "backend/ml/", "Failure prediction", "Risk score 0-100"],
        ["Alerts", "alerts.py + alerts/", "Notifications", "Email + Telegram delivery"],
        ["WebSocket", "websocket/", "Real-time push", "Live dashboard events"],
        ["Analytics", "analytics.py", "Uptime stats", "MTTR, reliability index"],
        ["Topology", "topology.py", "Network graph", "Switch-camera nodes/edges"],
    ])

    # ── 6. APPLICATION WORKFLOW ──
    h1(doc, "6. Application Workflow")
    diagram(doc, """
Application Starts (run-backend-logged.bat)
  ↓ init_db() — create tables, seed 25 demo cameras
  ↓ ensure_models() — train/load ML models
  ↓ Start: MonitorScheduler, WebSocket :8001, AlertScheduler, ModelScheduler, DB backup
  ↓ HTTP server on :8000
User opens http://127.0.0.1:8000 → Login → JWT token
  ↓ load() — parallel fetch 14 API endpoints
  ↓ Dashboard renders + WebSocket connects
Auto-refresh (30s/1m/5m/10m) → API calls → UI update
Background: Monitor detects change → Diagnosis → Incident → Telegram → WS push
""")

    # ── 7. DATA FLOW ──
    h1(doc, "7. Data Flow")
    diagram(doc, """
User → Frontend (fetch + Bearer JWT) → REST API (app.py)
  → require_auth() [protected routes]
  → Business Logic (diagnosis, ML, incidents)
  → SQLite (parameterized SQL)
  → JSON response → Frontend render → User

Parallel Monitoring Path:
MonitorScheduler → Ping/RTSP to camera IP → Health Classifier
  → Status change? → Diagnosis Engine → SQLite (diagnosis_history, incidents)
  → Telegram/Email + WebSocket dispatch → Browser
""")

    # ── 8. COMPONENT INTERACTION ──
    h1(doc, "8. Component Interaction")
    h2(doc, "WebSocket Event Types")
    table(doc, ["Event", "Trigger", "Frontend Action"], [
        ["CAMERA_OFFLINE", "Status → OFFLINE", "Update card, show live event"],
        ["CAMERA_ONLINE", "Status → ONLINE", "Green status, recovery notice"],
        ["STREAM_FAILURE", "RTSP unreachable", "Warning badge"],
        ["STREAM_RECOVERED", "RTSP restored", "Green stream status"],
        ["ALERT_CREATED", "New alert record", "Notification count update"],
    ])

    # ── 9. API DOCUMENTATION ──
    h1(doc, "9. API Documentation")
    p(doc, "Base URL: http://127.0.0.1:8000")
    h2(doc, "Authentication APIs")
    table(doc, ["Endpoint", "Method", "Auth", "Description"], [
        ["/api/auth/login", "POST", "No", "Login, receive JWT token"],
        ["/api/auth/logout", "POST", "No", "Logout response"],
        ["/api/auth/me", "GET", "Yes", "Current authenticated user"],
    ])
    h2(doc, "Camera APIs")
    table(doc, ["Endpoint", "Method", "Auth/Roles", "Description"], [
        ["GET /api/cameras", "GET", "No", "List all cameras"],
        ["POST /api/cameras", "POST", "ADMIN, NET_ENG", "Create camera + health check"],
        ["PUT /api/cameras/{id}", "PUT", "ADMIN, NET_ENG", "Update camera"],
        ["DELETE /api/cameras/{id}", "DELETE", "ADMIN", "Delete camera"],
        ["GET /api/cameras/stats", "GET", "No", "Health summary counts"],
        ["POST /api/monitor/tick", "POST", "ADMIN, NET_ENG", "Manual monitoring cycle"],
    ])
    h2(doc, "Intelligence APIs")
    table(doc, ["Endpoint", "Method", "Description"], [
        ["GET /api/diagnosis/history", "GET", "Root cause records"],
        ["GET /api/predictions", "GET", "Latest ML predictions"],
        ["POST /api/predictions/run", "POST", "Run ML prediction job"],
        ["GET /api/ml/statistics", "GET", "Model status and coverage"],
        ["GET /api/topology", "GET", "Network topology graph data"],
    ])
    h2(doc, "Reports & Analytics")
    table(doc, ["Endpoint", "Method", "Output"], [
        ["GET /api/reports/daily", "GET", "CSV download"],
        ["GET /api/reports/weekly", "GET", "CSV download"],
        ["GET /api/reports/monthly", "GET", "CSV download"],
        ["GET /api/analytics/system", "GET", "System uptime stats"],
        ["GET /api/root-cause/analytics", "GET", "Root cause statistics"],
    ])

    # ── 10. DATABASE DESIGN ──
    h1(doc, "10. Database Design")
    p(doc, "Engine: SQLite | File: backend/cc_camera_demo.db | Schema: backend/database.py")
    h2(doc, "Entity Relationship Diagram")
    diagram(doc, """
users ──→ user_activity
cameras ──→ ping_history, alerts, downtime_logs, predictions
cameras ──→ diagnosis_history, incidents, maintenance_sessions
cameras ──→ notification_history
incidents ──→ incident_notifications, incident_state_log, ai_feedback
maintenance_sessions ──→ maintenance_history

Key Tables:
  cameras (id PK, ip_address UNIQUE, status, latency_ms, switch_id, rtsp_url)
  users (id PK, username UNIQUE, password_hash, role)
  incidents (incident_id PK, camera_id FK, status, diagnosis, confidence)
  predictions (id PK, camera_id FK, risk_score, risk_level)
  diagnosis_history (id PK, camera_id FK, diagnosis, confidence, severity)
""")
    h2(doc, "Camera Status Values")
    table(doc, ["Status", "Meaning", "Typical Cause"], [
        ["ONLINE", "Healthy", "Ping OK, RTSP OK, latency normal"],
        ["OFFLINE", "Unreachable", "No ping response"],
        ["UNSTABLE", "Degraded", "Latency > 150ms or high packet loss"],
        ["STREAM_FAILURE", "Network OK, stream down", "RTSP port unavailable"],
    ])

    # ── 11. BUSINESS LOGIC ──
    h1(doc, "11. Business Logic")
    h2(doc, "Health Classification Algorithm")
    diagram(doc, """
IF ping fails          → OFFLINE
ELIF RTSP fails        → STREAM_FAILURE
ELIF latency > 150ms   → UNSTABLE
ELSE                   → ONLINE
""")
    h2(doc, "Diagnosis Decision Tree")
    diagram(doc, """
OFFLINE:
  packet_loss=100% + switch_ip → PoE Failure (82%)
  packet_loss=100%             → Power Failure (78%)
  else                         → Ethernet Cable Failure (68%)

STREAM_FAILURE:
  auth error in stream → Authentication Failure (86%)
  no RTSP URL          → RTSP Service Failure (88%)
  else                 → RTSP Service Failure (84%)

UNSTABLE:
  packet_loss >= 20%   → High Packet Loss (83%)
  latency >= 150ms     → High Latency (81%)
  else                 → Switch Port Failure (62%)
""")
    h2(doc, "ML Risk Scoring")
    p(doc, "Features extracted from last 200 ping_history samples. Random Forest (65%) + Isolation Forest (35%) combined into score 0-100. LOW (≤30), MEDIUM (≤60, 72hr window), HIGH (≤85, 24hr), CRITICAL (>85, 6hr).")
    h2(doc, "Incident Escalation")
    bullets(doc, ["First notification: immediately on failure", "First reminder: 6 hours later", "Subsequent reminders: every 3 hours", "Maintenance mode suppresses all alerts", "Switch-down: single alert if ALL cameras on switch offline"])

    # ── 12. TECHNOLOGY STACK ──
    h1(doc, "12. Technology Stack")
    table(doc, ["Category", "Technology", "Why Used", "Where"], [
        ["Frontend", "Vanilla HTML/CSS/JS", "No build step", "dist/index.html"],
        ["Backend", "Python 3 stdlib", "Zero dependencies", "backend/"],
        ["HTTP Server", "ThreadingHTTPServer", "Built-in, multi-threaded", "app.py"],
        ["Database", "SQLite", "File-based, zero config", "cc_camera_demo.db"],
        ["Auth", "Custom JWT + PBKDF2", "No external library", "auth.py"],
        ["ML", "scikit-learn (optional)", "Industry standard + fallback", "backend/ml/"],
        ["Real-time", "Custom WebSocket", "No package needed", "Port 8001"],
        ["Email", "smtplib (Gmail)", "Stdlib, reliable", "alerts.py"],
        ["Notifications", "Telegram Bot API", "Instant mobile alerts", "alerts.py"],
        ["Icons", "Tabler Icons CDN", "Professional UI", "Frontend"],
    ])

    # ── 13. THIRD-PARTY LIBRARIES ──
    h1(doc, "13. Third-Party Libraries")
    table(doc, ["Library", "Type", "Purpose", "Where"], [
        ["Google Fonts (Inter)", "CDN", "Typography", "Frontend head"],
        ["Tabler Icons", "CDN", "UI icons", "All pages"],
        ["scikit-learn", "Python (optional)", "RF + IsolationForest ML", "ml/trainer.py"],
        ["Gmail SMTP", "External API", "Daily email reports", "alerts.py"],
        ["Telegram Bot API", "External API", "Instant alerts", "alerts.py"],
    ])
    p(doc, "npm dependencies: None. Python pip dependencies: None required (stdlib-only backend).")

    # ── 14. FLOW DIAGRAMS ──
    h1(doc, "14. Application Flow Diagrams")
    h2(doc, "Login Sequence")
    diagram(doc, """
User → Frontend: Enter credentials
Frontend → API: POST /api/auth/login {username, password}
API → SQLite: SELECT user WHERE username=?
API → auth.py: verify_password(plain, PBKDF2 hash)
API → auth.py: create_token(id, username, role) → JWT
API → Frontend: {token, user}
Frontend → sessionStorage: store authToken
Frontend → API: GET /api/cameras/stats (parallel load)
Frontend → User: Dashboard displayed
""")
    h2(doc, "Monitoring Cycle")
    diagram(doc, """
[Timer 30s] → Fetch all cameras
  → For each: Ping → RTSP → Classify health
  → Update cameras + ping_history
  → Status changed?
      YES → Diagnose → Record diagnosis_history
          → Create/update incident
          → In maintenance? → Skip notify
          → Else → Send Telegram
          → WebSocket dispatch
      NO → Next camera
  → Wait 30s → Repeat
""")
    h2(doc, "Deployment Diagram")
    diagram(doc, """
Campus Network                    Operations Server
┌─────────────┐                  ┌──────────────────────┐
│ Camera IPs  │◄── Ping/RTSP ───│ Python Backend :8000  │
│ Switches    │                  │ WebSocket :8001       │
└─────────────┘                  │ cc_camera_demo.db     │
                                 └──────────┬───────────┘
                                            │
              ┌─────────────────────────────┼──────────────┐
              ▼                             ▼              ▼
         Browser Dashboard            Telegram App    Email Inbox
""")

    # ── 15. FEATURE-BY-FEATURE ──
    h1(doc, "15. Feature-by-Feature Explanation")
    table(doc, ["Feature", "User Action", "Backend", "Database", "Possible Errors"], [
        ["Dashboard", "View on login", "14 parallel API calls", "cameras, predictions", "Backend unreachable"],
        ["Camera Cards", "Browse/filter", "GET /api/cameras", "cameras table", "Empty if no cameras"],
        ["Add Camera", "Fill form", "POST + health check", "INSERT cameras", "Duplicate IP error"],
        ["Topology", "View canvas map", "GET /api/topology", "Aggregate by switch", "No data to draw"],
        ["Diagnosis", "View AI section", "Rule engine", "diagnosis_history", "Unknown Failure fallback"],
        ["ML Predictions", "View risk table", "RF + IF scoring", "ping_history, predictions", "PENDING if no model"],
        ["Alerts", "Read-only view", "IncidentService", "incidents, notifications", "SKIPPED if .env missing"],
        ["Maintenance", "Start/complete", "MaintenanceService", "maintenance_sessions", "Auto-restore on expiry"],
        ["CSV Reports", "Download", "reports.py", "downtime_logs", "Empty CSV if no data"],
        ["Global Search", "Ctrl+K", "Client-side search", "Loaded data in memory", "No results found"],
        ["WebSocket", "Live events panel", "WS :8001", "—", "Disconnected state"],
    ])

    # ── 16. SECURITY ──
    h1(doc, "16. Security Design")
    table(doc, ["Area", "Implementation"], [
        ["Authentication", "JWT (HMAC-SHA256), 8-hour expiry, sessionStorage"],
        ["Password", "PBKDF2-HMAC-SHA256, 100k iterations, timing-safe compare"],
        ["Authorization", "RBAC: ADMINISTRATOR, NETWORK_ENGINEER, OPERATOR, VIEWER"],
        ["SQL Injection", "Parameterized queries throughout (? placeholders)"],
        ["Secret Handling", ".env only; settings API strips tokens/passwords"],
        ["API Protection", "require_auth() on all write operations"],
        ["CSRF", "Not implemented (JWT in header, localhost deployment)"],
    ])
    h2(doc, "Role Permissions Matrix")
    table(doc, ["Action", "ADMIN", "NET_ENG", "OPERATOR", "VIEWER"], [
        ["View dashboard", "Yes", "Yes", "Yes", "Yes"],
        ["Add/edit cameras", "Yes", "Yes", "No", "No"],
        ["Delete cameras", "Yes", "No", "No", "No"],
        ["Run monitor tick", "Yes", "Yes", "No", "No"],
        ["Update settings", "Yes", "No", "No", "No"],
        ["User management", "Yes", "No", "No", "No"],
    ])

    # ── 17. PERFORMANCE ──
    h1(doc, "17. Performance")
    table(doc, ["Operation", "Expected Time"], [
        ["API health check", "< 10ms"],
        ["Camera list (25 cameras)", "< 30ms"],
        ["Dashboard parallel load", "< 200ms"],
        ["Monitor tick (25 cameras)", "1-5 seconds"],
        ["ML prediction run", "< 500ms"],
    ])
    h2(doc, "Bottlenecks & Mitigations")
    table(doc, ["Bottleneck", "Mitigation"], [
        ["Sequential ping of all cameras", "Acceptable for <100 cameras; parallel workers for scale"],
        ["SQLite concurrent writes", "Enable WAL mode; migrate to PostgreSQL at scale"],
        ["Monolithic 109KB HTML", "Acceptable for LAN; restore React build pipeline"],
    ])

    # ── 18. DEPLOYMENT ──
    h1(doc, "18. Deployment")
    h2(doc, "Quick Start")
    diagram(doc, """
cd "C:\\Users\\Intel\\OneDrive\\문서\\Projects\\cc-camera-frontend-only"
.\\run-backend-logged.bat
Open: http://127.0.0.1:8000
Login: admin / Admin@1234
""")
    h2(doc, "Environment Variables (.env)")
    table(doc, ["Variable", "Purpose"], [
        ["DATABASE_PATH", "SQLite file path"],
        ["GMAIL_USER", "SMTP sender email"],
        ["GMAIL_APP_PASSWORD", "Gmail app password"],
        ["ADMIN_EMAIL", "Alert recipient"],
        ["TELEGRAM_BOT_TOKEN", "Telegram bot token"],
        ["TELEGRAM_CHAT_ID", "Telegram destination chat"],
        ["JWT_SECRET", "Token signing secret"],
    ])
    h2(doc, "Server Requirements")
    table(doc, ["Requirement", "Minimum"], [
        ["OS", "Windows 10/11 or Linux"],
        ["Python", "3.8+"],
        ["RAM", "512 MB"],
        ["Network", "Access to camera subnet"],
        ["Browser", "Chrome or Edge"],
    ])

    # ── 19. CODE WALKTHROUGH ──
    h1(doc, "19. Code Walkthrough")
    table(doc, ["File", "Key Functions/Classes", "Purpose"], [
        ["backend/app.py", "Handler, main(), create_camera()", "HTTP server, all routes"],
        ["backend/auth.py", "hash_password(), create_token(), require_auth()", "JWT authentication"],
        ["backend/database.py", "init_db(), connect(), DEMO_CAMERAS", "Schema + demo seed"],
        ["backend/diagnosis_engine.py", "diagnose_camera(), RECOMMENDATIONS", "Root cause analysis"],
        ["monitoring/monitor_scheduler.py", "MonitorScheduler.run_once()", "30s monitoring loop"],
        ["monitoring/health_classifier.py", "classify_health()", "Status normalization"],
        ["ml/feature_extractor.py", "extract_features()", "15 ML features from ping history"],
        ["ml/predictor.py", "predict_risk()", "Score camera failure risk"],
        ["incidents.py", "IncidentService", "Incident lifecycle + Telegram"],
        ["dist/index.html", "api(), load(), renderCameras()", "Complete frontend SPA"],
    ])

    # ── 20. DESIGN DECISIONS ──
    h1(doc, "20. Design Decisions")
    table(doc, ["Decision", "Why", "Trade-off", "Alternative"], [
        ["Python stdlib only", "Zero pip install", "Less feature-rich", "Flask + SQLAlchemy"],
        ["SQLite", "Single file backup", "No concurrent writes", "PostgreSQL"],
        ["Monolithic HTML", "No build pipeline", "Hard to maintain", "React/Vite"],
        ["Rule-based diagnosis", "Explainable results", "Less accurate than ML", "Pure ML classifier"],
        ["30s monitor interval", "Balance speed vs load", "Miss sub-30s outages", "5s interval"],
        ["Automatic-only alerts", "Prevent spam", "No manual test", "Manual trigger option"],
    ])

    # ── 21. INTERVIEW QUESTIONS ──
    h1(doc, "21. Possible Interview Questions")
    h2(doc, "Basic")
    h3(doc, "Q: What does your project do?")
    p(doc, "It monitors campus CCTV camera health — checking network reachability, latency, and RTSP stream status. When a camera fails, it automatically diagnoses the root cause, sends alerts, and shows everything on an enterprise dashboard.")
    h3(doc, "Q: What technologies did you use?")
    p(doc, "Python backend with stdlib HTTP server, SQLite database, vanilla JavaScript frontend, JWT authentication, and optional scikit-learn for ML predictions.")
    h3(doc, "Q: What are the camera status types?")
    p(doc, "ONLINE (healthy), OFFLINE (no ping), UNSTABLE (high latency), STREAM_FAILURE (ping OK but RTSP unavailable).")
    h2(doc, "Intermediate")
    h3(doc, "Q: Explain the monitoring workflow.")
    p(doc, "A background scheduler runs every 30 seconds. For each camera, it pings the IP and checks RTSP. If status changes, the diagnosis engine determines root cause, an incident is created, and Telegram/email alerts are sent automatically.")
    h3(doc, "Q: How does the diagnosis engine work?")
    p(doc, "Rule-based logic examining status, latency, packet loss, and stream errors. Example: OFFLINE + 100% packet loss + switch IP → PoE Failure at 82% confidence with specific maintenance steps.")
    h3(doc, "Q: Explain the ML module.")
    p(doc, "Features from last 200 ping samples (latency, packet loss, anomaly rate). Random Forest + Isolation Forest combine (65/35) into 0-100 risk score mapped to LOW/MEDIUM/HIGH/CRITICAL.")
    h2(doc, "Advanced")
    h3(doc, "Q: How would you scale to 1000 cameras?")
    p(doc, "PostgreSQL, worker processes with job queue (Celery), connection pooling, camera sharding, Redis caching, load balancer with shared DB.")
    h3(doc, "Q: Why rule-based diagnosis instead of ML?")
    p(doc, "Rules are explainable — maintenance teams need auditable logic. ML complements for proactive risk, but operational diagnosis requires deterministic reasoning.")
    h3(doc, "Q: How does switch-aware alerting work?")
    p(doc, "Cameras grouped by switch_id. If ALL cameras on a switch are offline, one switch-level alert is sent instead of individual camera alerts.")

    # ── 22. PRESENTATION GUIDE ──
    h1(doc, "22. Presentation Guide")
    h2(doc, "5-Minute Presentation")
    bullets(doc, [
        "Problem (30s): Campus cameras fail silently; maintenance is reactive",
        "Solution (30s): Automated monitoring with intelligent diagnosis",
        "Demo (2m): Login → Dashboard → offline camera → diagnosis → topology → alert",
        "Tech (1m): Python + SQLite + vanilla JS, JWT auth, ML predictions",
        "Impact (1m): 30-second detection, automatic Telegram alerts, CSV reports",
    ])
    h2(doc, "10-Minute Presentation")
    p(doc, "Add: architecture diagram, monitoring workflow, ML demo, RBAC, maintenance mode, live WebSocket event.")
    h2(doc, "20-Minute Presentation")
    p(doc, "Add: module breakdown, ER diagram, diagnosis decision tree, incident lifecycle, security design, API walkthrough, deployment checklist, future enhancements, Q&A.")

    # ── 23. CLIENT EXPLANATION ──
    h1(doc, "23. Client Explanation (Non-Technical)")
    p(doc, "Think of this as a health checkup system for your campus security cameras. Just like a doctor monitors heartbeat and blood pressure, this system continuously checks whether each camera is reachable, responding quickly, and streaming video properly.")
    p(doc, "When something goes wrong — say a camera in the Admin Block stops working — the system doesn't just say 'Camera offline.' It tells your maintenance team the most likely reason (power issue, network cable, switch failure) and exactly what to check first.")
    p(doc, "Your team gets instant alerts on Telegram for urgent problems, and a daily email summary. Everything is visible on a clean dashboard with green (healthy), orange (warning), and red (offline) status. It works with your existing cameras — it doesn't replace your video recording system.")

    # ── 24. FUTURE ENHANCEMENTS ──
    h1(doc, "24. Future Enhancements")
    table(doc, ["Area", "Enhancement"], [
        ["Performance", "SQLite WAL mode, Redis caching, parallel ping workers"],
        ["UI/UX", "Restore React component architecture, mobile PWA"],
        ["Scalability", "PostgreSQL, Celery job queue, multi-campus tenants"],
        ["AI", "Deep learning video quality analysis, ONVIF integration"],
        ["Security", "HTTPS, rate limiting, 2FA, CSRF protection"],
        ["Cloud", "Docker Compose, Azure/AWS VM, CI/CD pipeline"],
        ["Reporting", "PDF reports, SLA dashboards, scheduled email customization"],
    ])

    # ── 25. PROJECT SUMMARY ──
    h1(doc, "25. Project Summary")
    h2(doc, "One-Paragraph Summary")
    p(doc, "The UCEK-JNTUK Camera Health Monitoring System is a full-stack campus surveillance monitoring platform that proactively checks CCTV camera network reachability, latency, and RTSP stream health every 30 seconds. Built with Python, SQLite, and vanilla JavaScript, it features intelligent rule-based root cause diagnosis, ML-powered failure risk predictions, automatic Telegram and email notifications, incident lifecycle management, network topology visualization, and role-based JWT authentication.")
    h2(doc, "Resume Description")
    p(doc, "Developed a full-stack CCTV health monitoring platform using Python, SQLite, and vanilla JavaScript serving 25+ campus cameras. Implemented automated ICMP/RTSP health checks, rule-based diagnosis engine with 12 root-cause categories, ML risk prediction (Random Forest + Isolation Forest), JWT authentication with RBAC, WebSocket real-time updates, and automatic Telegram/email alerting with incident lifecycle management.")
    h2(doc, "LinkedIn Description")
    p(doc, "Built an enterprise camera health monitoring system for campus CCTV infrastructure at UCEK-JNTUK. The platform automates network health checks, intelligently diagnoses failures, predicts camera failure risk using ML, and delivers real-time alerts via Telegram. Features include network topology mapping, CSV reporting, maintenance mode, and a role-based dashboard.")
    h2(doc, "Strengths vs Weaknesses")
    table(doc, ["Strengths", "Weaknesses"], [
        ["Works immediately with demo data", "Monolithic frontend hard to maintain"],
        ["Zero pip dependencies", "No automated tests"],
        ["Intelligent diagnosis + ML", "Demo IPs use simulated ping"],
        ["Comprehensive documentation", "No Docker/CI pipeline"],
        ["Switch-aware alerting", "Localhost-only binding"],
        ["Full audit trail", "No CSRF protection"],
    ])

    return doc


def convert_to_pdf(docx_path: Path, pdf_path: Path) -> bool:
    try:
        from docx2pdf import convert
        convert(str(docx_path), str(pdf_path))
        return pdf_path.exists()
    except Exception as exc:
        print(f"DOCX→PDF via Word failed: {exc}", file=sys.stderr)
        return False


def convert_to_pdf_fpdf(docx_path: Path, pdf_path: Path) -> bool:
    """Fallback PDF using fpdf2 (text-only, no complex formatting)."""
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "UCEK-JNTUK Camera Health Monitoring System", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "Complete Project Guide - See DOCX for full formatted version", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, (
            "This PDF is a lightweight export. For full diagrams, tables, and formatting, "
            "open UCEK-JNTUK_Project_Complete_Guide.docx or the HTML version "
            "(UCEK-JNTUK_Project_Complete_Guide.html) and use Print to PDF from your browser."
        ))
        pdf.output(str(pdf_path))
        return pdf_path.exists()
    except Exception as exc:
        print(f"FPDF fallback failed: {exc}", file=sys.stderr)
        return False


def main() -> None:
    print("Building DOCX document...")
    doc = build_document()
    doc.save(str(DOCX_PATH))
    print(f"DOCX saved: {DOCX_PATH}")

    print("Converting to PDF...")
    if convert_to_pdf(DOCX_PATH, PDF_PATH):
        print(f"PDF saved: {PDF_PATH}")
    else:
        print("Word-based PDF conversion unavailable. Creating reference PDF...")
        if convert_to_pdf_fpdf(DOCX_PATH, PDF_PATH):
            print(f"Reference PDF saved: {PDF_PATH}")
        else:
            print("PDF generation failed. Use the HTML file and Print to PDF from browser.")

    html_path = OUTPUT_DIR / "UCEK-JNTUK_Project_Complete_Guide.html"
    if html_path.exists():
        print(f"HTML (best diagrams): {html_path}")


if __name__ == "__main__":
    main()
