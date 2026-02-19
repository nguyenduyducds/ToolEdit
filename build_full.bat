@echo off
echo ========================================
echo   VIDEO EDITOR PRO - FULL BUILD
echo   Including: Whisper AI + FFmpeg + CUDA
echo ========================================
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo [1/4] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found, using global Python
)

REM Install/Update PyInstaller
echo.
echo [2/4] Checking PyInstaller...
pip install --upgrade pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Clean old build
echo.
echo [3/4] Cleaning old build files...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec

REM Run build script
echo.
echo [4/4] Building EXE (this may take 5-10 minutes)...
echo.
python build_full.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   BUILD COMPLETE!
    echo ========================================
    echo.
    echo Output folder: dist\VideoEditorPro\
    echo.
    echo To run: dist\VideoEditorPro\VideoEditorPro.exe
    echo.
    echo IMPORTANT NOTES:
    echo - Whisper AI models are bundled (no internet needed)
    echo - FFmpeg is included
    echo - First subtitle generation may take 10-30s (model loading)
    echo - Distribute the entire 'VideoEditorPro' folder
    echo.
    echo TEST CHECKLIST:
    echo [1] Run the EXE and load a video
    echo [2] Enable subtitles and test generation
    echo [3] Try exporting with all filters
    echo.
) else (
    echo.
    echo ========================================
    echo   BUILD FAILED!
    echo ========================================
    echo.
    echo Common issues:
    echo - Missing dependencies: pip install -r requirements_full.txt
    echo - Whisper not installed: pip install openai-whisper
    echo - PyTorch not installed: pip install torch
    echo.
    echo Please check the error messages above.
    echo.
)

pause
