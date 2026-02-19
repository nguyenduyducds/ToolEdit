@echo off
echo ========================================
echo Video Editor Pro - Quick Start Setup
echo ========================================
echo.

REM Check if venv exists
if exist "venv\" (
    echo [OK] Virtual environment already exists
) else (
    echo [*] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created!
)

echo.
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

echo [OK] Virtual environment activated!
echo.

echo [*] Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To run the application:
echo   python main.py
echo.
echo To deactivate virtual environment:
echo   deactivate
echo.

pause
