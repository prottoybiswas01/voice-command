# PowerShell Launcher for X Assistant Phase 6
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " Starting X Assistant Phase 6 Personal AI Ecosystem" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

if (-not (Test-Path "venv")) {
    Write-Host "Error: Virtual environment not found! Please run setup.bat first." -ForegroundColor Red
    Pause
    Exit
}

Write-Host "Launching X Assistant main process..." -ForegroundColor Green
& ".\venv\Scripts\python.exe" main.py
