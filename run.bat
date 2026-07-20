@echo off
TITLE X Assistant Phase 6 - Launcher
echo ===================================================
echo Starting X Assistant Phase 6 Personal AI Ecosystem...
echo ===================================================

IF NOT EXIST "venv" (
    echo Error: Virtual environment not found! Please run setup.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting X Assistant main process...
.\venv\Scripts\python.exe main.py

pause
