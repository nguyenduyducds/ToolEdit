@echo off
chcp 65001 >nul
title Building VideoEditorPro
color 0A

echo ════════════════════════════════════════════════════════
echo      VIDEO EDITOR PRO - BUILD EXE
echo ════════════════════════════════════════════════════════
echo.

REM Activate venv
echo [1/4] Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

REM Install PyInstaller
echo.
echo [2/4] Installing PyInstaller...
pip install --upgrade pyinstaller

REM Clean
echo.
echo [3/4] Cleaning old builds...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
del /q *.spec 2>nul

REM Build
echo.
echo [4/4] Building EXE (This will take 5-10 minutes)...
echo ────────────────────────────────────────────────────────

pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "VideoEditorPro" ^
    --add-data "Model;Model" ^
    --add-data "config;config" ^
    --add-data "core;core" ^
    --add-data "UI;UI" ^
    --add-data "utils;utils" ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageTk ^
    --hidden-import cv2 ^
    --hidden-import numpy ^
    --collect-all imageio_ffmpeg ^
    --clean ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ════════════════════════════════════════════════════════
    echo      BUILD FAILED!
    echo ════════════════════════════════════════════════════════
    echo.
    echo Common fixes:
    echo 1. pip install -r requirements.txt
    echo 2. Make sure you're in the project root directory
    echo 3. Try build_simple.bat instead
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════
echo      BUILD SUCCESS!
echo ════════════════════════════════════════════════════════
echo.
echo File: dist\VideoEditorPro.exe
echo.
echo You can now copy this EXE to any Windows PC!
echo.

explorer dist
pause
