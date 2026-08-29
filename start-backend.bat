@echo off
cd /d "%~dp0"
echo Starting backend. Close this window or press Ctrl+C to stop alerts.
start "" "http://127.0.0.1:8000"
python backend\app.py
pause
