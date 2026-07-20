@echo off
TITLE X Assistant - Virtual Environment Setup
echo ===================================================
echo Setting up Python Virtual Environment for X Assistant...
echo ===================================================

IF NOT EXIST "venv" (
    echo Creating virtual environment 'venv'...
    python -m venv venv
    echo Virtual environment created successfully.
) ELSE (
    echo Virtual environment 'venv' already exists.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Setup completed successfully! Run install.bat to install packages.
pause
