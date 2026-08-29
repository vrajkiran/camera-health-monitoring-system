@echo off
cd /d "%~dp0"
echo Starting UCEK-JNTUK Camera Health backend...
echo Close this window or press Ctrl+C to stop monitoring and Telegram alerts.
start "" "http://127.0.0.1:8000"
python backend\app.py
echo.
echo Backend stopped. Alerts are no longer running.
pause
