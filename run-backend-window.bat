@echo off
cd /d "%~dp0"
echo Starting CC Camera backend...
echo Dashboard: http://127.0.0.1:8000
python backend\run_forever.py
echo.
echo Backend stopped. Press any key to close this window.
pause >nul
