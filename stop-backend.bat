@echo off
echo Stopping UCEK-JNTUK Camera Health backend...
for /f "tokens=2 delims=," %%P in ('wmic process where "name='python.exe' and commandline like '%%backend\\app.py%%'" get processid /format:csv ^| findstr /r "[0-9]"') do taskkill /PID %%P /F >nul 2>nul
for /f "tokens=2 delims=," %%P in ('wmic process where "name='python.exe' and commandline like '%%run_forever.py%%'" get processid /format:csv ^| findstr /r "[0-9]"') do taskkill /PID %%P /F >nul 2>nul
echo Backend stop command completed.
pause
