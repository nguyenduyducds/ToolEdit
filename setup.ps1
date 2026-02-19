# Quick Start Script for Video Editor Pro
# Run this script to setup everything automatically

Write-Host "🎬 Video Editor Pro - Quick Start Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
} else {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created!" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow

# Activate venv
& ".\venv\Scripts\Activate.ps1"

Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Check if packages are installed
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow

$packages = @(
    "tkinterdnd2",
    "moviepy",
    "openai-whisper",
    "SpeechRecognition",
    "imageio-ffmpeg",
    "pillow",
    "numpy",
    "scipy",
    "psutil",
    "requests"
)

$needInstall = $false

foreach ($package in $packages) {
    $installed = pip show $package 2>$null
    if ($installed) {
        Write-Host "  ✅ $package" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $package (not installed)" -ForegroundColor Red
        $needInstall = $true
    }
}

Write-Host ""

if ($needInstall) {
    Write-Host "📥 Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "✅ All dependencies already installed!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "  python main.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "To deactivate virtual environment:" -ForegroundColor Cyan
Write-Host "  deactivate" -ForegroundColor Yellow
Write-Host ""
