@echo off
TITLE X Assistant - Package Installer
echo ===================================================
echo Installing X Assistant Dependencies on Windows...
echo ===================================================

IF NOT EXIST "venv" (
    echo Virtual environment not found! Running setup.bat first...
    call setup.bat
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing required Python packages from requirements.txt...
pip install -r requirements.txt

echo Installing PyAudio (optional microphone audio engine)...
pip install pyaudio --only-binary=:all: || echo [Note] PyAudio binary wheel not available for this Python version. Microphone fallback enabled.

echo Installing Playwright dependencies...
playwright install chromium

echo ===================================================
echo All dependencies installed successfully!
echo Run run.bat to launch X Assistant.
echo ===================================================
pause
