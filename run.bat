@echo off
TITLE X Assistant - Launcher
echo ===================================================
echo Starting X Assistant (Phase-1)...
echo ===================================================

IF NOT EXIST "venv" (
    echo Error: Virtual environment not found! Please run setup.bat and install.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting X Assistant main process...
python main.py

pause
