@echo off
setlocal enabledelayedexpansion

REM Amazon Buy Box Analyzer - GUI Entry Point
REM This script launches the graphical user interface:
REM 1.) Changes to project directory
REM 2.) Activates virtual environment
REM 3.) Updates dependencies
REM 4.) Launches the Tkinter GUI

echo ========================================
echo Amazon Buy Box Analyzer - GUI Mode
echo ========================================
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Navigate to project root (one level up from main/)
cd /d "%SCRIPT_DIR%.."

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [OK] Found virtual environment
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [OK] Found virtual environment
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found!
    echo Please create one with: python -m venv venv
    pause
    exit /b 1
)

REM Update dependencies
echo.
echo [INFO] Installing/updating dependencies...
pip install -r requirements.txt --quiet

REM Launch the GUI
echo.
echo [INFO] Launching Buy Box Analyzer GUI...
echo [INFO] Close the GUI window to exit
echo ========================================
echo.

python main/tool.py

echo.
echo ========================================
echo [INFO] GUI closed
echo ========================================
