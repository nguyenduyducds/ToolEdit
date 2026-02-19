@echo off
chcp 65001 >nul
title Building Video Editor Pro
color 0A

echo ╔════════════════════════════════════════════════════════════╗
echo ║     VIDEO EDITOR PRO - BUILD PROCESS                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Activate venv
echo [1/5] Kích hoạt môi trường ảo...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Không tìm thấy virtual environment!
    pause
    exit /b 1
)

REM Install PyInstaller
echo.
echo [2/5] Cài đặt PyInstaller...
pip install --upgrade pyinstaller >nul 2>&1

REM Clean
echo.
echo [3/5] Dọn dẹp build cũ...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
del /q *.spec 2>nul

REM Build
echo.
echo [4/5] Bắt đầu build (Vui lòng đợi 5-10 phút)...
echo ────────────────────────────────────────────────────────────

pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "VideoEditorPro" ^
    --add-data "Model;Model" ^
    --add-data "config;config" ^
    --add-data "core;core" ^
    --add-data "UI;UI" ^
    --add-data "utils;utils" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "PIL.ImageTk" ^
    --hidden-import "cv2" ^
    --hidden-import "numpy" ^
    --collect-all "imageio_ffmpeg" ^
    --clean ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [FAILURE] Build thất bại!
    echo.
    echo Lỗi thường gặp:
    echo - Thiếu thư viện: pip install -r requirements.txt
    echo - Lỗi đường dẫn: Đảm bảo chạy từ thư mục gốc project
    echo.
    pause
    exit /b 1
)

REM Success
echo.
echo [5/5] Hoàn tất!
echo ╔════════════════════════════════════════════════════════════╗
echo ║                  BUILD THÀNH CÔNG!                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo File: dist\VideoEditorPro.exe
echo.

explorer dist
pause
