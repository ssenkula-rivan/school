@echo off
REM School Management System Launcher for Windows

echo ============================================================
echo School Management System
echo ============================================================
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Navigate to project root (2 levels up)
cd /d "%SCRIPT_DIR%..\.."

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Run the launcher
python "%SCRIPT_DIR%launcher.py"

pause
