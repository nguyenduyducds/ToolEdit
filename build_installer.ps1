# Build Installer Script for Video Editor Pro
# Automatically builds EXE and creates installer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Video Editor Pro - Build Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build EXE
Write-Host "[1/3] Building EXE with PyInstaller..." -ForegroundColor Yellow
python build_final.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build EXE!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ EXE built successfully!" -ForegroundColor Green
Write-Host ""

# Step 2: Check if Inno Setup is installed
Write-Host "[2/3] Checking Inno Setup..." -ForegroundColor Yellow

$InnoSetupPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe"
)

$ISCC = $null
foreach ($path in $InnoSetupPaths) {
    if (Test-Path $path) {
        $ISCC = $path
        break
    }
}

if (-not $ISCC) {
    Write-Host "❌ Inno Setup not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Inno Setup from:" -ForegroundColor Yellow
    Write-Host "https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found Inno Setup: $ISCC" -ForegroundColor Green
Write-Host ""

# Step 3: Build Installer
Write-Host "[3/3] Building Installer..." -ForegroundColor Yellow

& $ISCC "VideoEditorPro_Setup.iss"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build installer!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installer location:" -ForegroundColor Cyan
Write-Host "  installer\VideoEditorPro_Setup_v2.0.2.exe" -ForegroundColor White
Write-Host ""
Write-Host "You can now distribute this installer!" -ForegroundColor Yellow
Write-Host ""

# Open installer folder
$response = Read-Host "Open installer folder? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    explorer.exe "installer"
}
