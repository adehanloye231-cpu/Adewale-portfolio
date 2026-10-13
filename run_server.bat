@echo off
chcp 65001 >nul
echo ============================================================
echo   ADEWALE PORTFOLIO - BACKEND SERVER LAUNCHER
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
py --version
if errorlevel 1 (
    echo ERROR: Python is not installed! Please install Python from python.org
    pause
    exit /b 1
)

echo.
echo [2/3] Installing dependencies (Flask + flask-cors)...
py -m pip install --upgrade pip
py -m pip install -r backend\requirements.txt
if errorlevel 1 (
    echo.
    echo WARNING: Dependencies may already be installed, continuing...
)

echo.
echo [3/3] Starting Portfolio Backend Server...
echo.
echo   Website:   http://localhost:5000/
echo   Admin:     http://localhost:5000/admin  (password: admin123)
echo   API:       POST http://localhost:5000/api/contact
echo   Data file: backend\data\contact_submissions.json
echo.
echo   Press Ctrl+C to stop the server
echo ============================================================
echo.

py backend\app.py

pause
