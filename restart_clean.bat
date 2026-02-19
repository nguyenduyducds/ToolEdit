@echo off
echo ========================================
echo   Video Editor Pro - Clean Restart
echo ========================================
echo.

echo [1/4] Stopping any running instances...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Video Editor Pro*" 2>nul
timeout /t 1 /nobreak >nul

echo [2/4] Cleaning Python cache...
if exist "__pycache__" rd /s /q "__pycache__"
if exist "UI\__pycache__" rd /s /q "UI\__pycache__"
if exist "UI\modules\__pycache__" rd /s /q "UI\modules\__pycache__"
if exist "utils\__pycache__" rd /s /q "utils\__pycache__"
if exist "core\__pycache__" rd /s /q "core\__pycache__"
echo    ✓ Cache cleared

echo [3/4] Cleaning temporary files...
if exist "*.pyc" del /q "*.pyc"
if exist "UI\*.pyc" del /q "UI\*.pyc"
if exist "utils\*.pyc" del /q "utils\*.pyc"
echo    ✓ Temp files cleaned

echo [4/4] Starting Video Editor Pro...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ❌ Error occurred! Press any key to exit...
    pause >nul
)
