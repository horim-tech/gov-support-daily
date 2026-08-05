@echo off
cd /d "%~dp0"

echo [1/3] Collecting today's announcements...
pushd scraper
"C:\Users\1\AppData\Local\Python\bin\python.exe" main.py
popd

echo.
echo [2/3] Starting dashboard server...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1

cd /d "%~dp0web"
start "GovSupportDashboard" /min cmd /c "npm run start"

echo [3/3] Opening browser...
ping -n 5 127.0.0.1 >nul
start http://localhost:3000

exit
