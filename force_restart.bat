@echo off
echo ========================================
echo   FORCE CLEAN RESTART
echo ========================================
echo.

echo [1/6] Killing ALL Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 /nobreak >nul
echo    ✓ All Python processes stopped

echo [2/6] Cleaning Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo    ✓ Python cache cleared

echo [3/6] Cleaning .pyc files...
del /s /q *.pyc 2>nul
echo    ✓ Bytecode files removed

echo [4/6] Cleaning CustomTkinter cache...
if exist "%USERPROFILE%\.customtkinter" rd /s /q "%USERPROFILE%\.customtkinter"
if exist "%APPDATA%\customtkinter" rd /s /q "%APPDATA%\customtkinter"
echo    ✓ CustomTkinter cache cleared

echo [5/6] Cleaning temp files...
if exist "*.log" del /q "*.log"
if exist "temp_*" del /q "temp_*"
echo    ✓ Temp files removed

echo [6/6] Starting with FRESH environment...
echo.
set PYTHONDONTWRITEBYTECODE=1
python -B main.py

if errorlevel 1 (
    echo.
    echo ❌ Error! Press any key...
    pause >nul
)
