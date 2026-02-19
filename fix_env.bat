@echo off
setlocal
echo ===================================================
echo      FIXING PYTHON ENVIRONMENT - USER: Admin
echo ===================================================

REM Define expected Python path
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"

REM Validate Python 3.10 existence
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Could not find Python 3.10 at: %PYTHON_EXE%
    echo Checking global PATH for python...
    where python
    pause
    exit /b 1
)

echo [INFO] Found Python 3.10 at: %PYTHON_EXE%

REM Backup old venv
if exist "venv" (
    echo [INFO] Moving old venv to venv_old...
    if exist "venv_old" rmdir /s /q "venv_old"
    rename "venv" "venv_old"
)

REM Create new venv
echo [INFO] Creating new virtual environment...
"%PYTHON_EXE%" -m venv venv

REM Activate and Install
echo [INFO] Activating venv and installing requirements...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ===================================================
echo      SETUP COMPLETE - STARTING APP
echo ===================================================
python main.py
pause
