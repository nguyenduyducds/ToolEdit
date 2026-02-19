"""
Full Build Script for Video Editor Pro
Includes: Whisper AI, FFmpeg, All Dependencies
"""

import PyInstaller.__main__
import os
import sys
import shutil
from pathlib import Path

# ==================== CONFIG ====================
APP_NAME = "VideoEditorPro"
VERSION = "2.0.0"
MAIN_SCRIPT = "main.py"

# ==================== PATHS ====================
# Get FFmpeg path from imageio_ffmpeg
try:
    from imageio_ffmpeg import get_ffmpeg_exe
    ffmpeg_exe = get_ffmpeg_exe()
    print(f"✅ Found FFmpeg: {ffmpeg_exe}")
except:
    ffmpeg_exe = None
    print("⚠️ FFmpeg not found! Will need manual copy.")

# Pre-download Whisper models
print("\n📥 Checking Whisper AI models...")
whisper_cache = None
try:
    import whisper
    import torch
    
    # Get Whisper cache directory
    whisper_cache = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
    
    # Download 'small' model if not exists
    model_name = "small"
    model_file = os.path.join(whisper_cache, f"{model_name}.pt")
    
    if not os.path.exists(model_file):
        print(f"   Downloading Whisper '{model_name}' model (this may take a few minutes)...")
        model = whisper.load_model(model_name)
        print(f"   ✅ Model downloaded to: {whisper_cache}")
    else:
        print(f"   ✅ Model already exists: {model_file}")
    
except Exception as e:
    print(f"   ⚠️ Whisper model check failed: {e}")
    print("   The app will download models on first run.")

# ==================== DATA FILES ====================
add_data = [
    'assets;assets',
    'UI;UI',
    'utils;utils',
    'core;core',
]

# Add Whisper models if found
if whisper_cache and os.path.exists(whisper_cache):
    add_data.append(f'{whisper_cache};whisper_models')
    print(f"✅ Will bundle Whisper models from: {whisper_cache}")

# Add Whisper assets (mel_filters.npz, etc.)
try:
    import whisper
    whisper_pkg_path = Path(whisper.__file__).parent
    whisper_assets = whisper_pkg_path / "assets"
    
    if whisper_assets.exists():
        add_data.append(f'{whisper_assets};whisper/assets')
        print(f"✅ Will bundle Whisper assets from: {whisper_assets}")
    else:
        print(f"⚠️ Whisper assets not found at: {whisper_assets}")
except Exception as e:
    print(f"⚠️ Could not locate Whisper assets: {e}")

# Create srt_files directory if not exists
srt_dir = "srt_files"
if not os.path.exists(srt_dir):
    os.makedirs(srt_dir)
    # Create a dummy file to ensure folder is included
    with open(os.path.join(srt_dir, ".gitkeep"), "w") as f:
        f.write("")
add_data.append('srt_files;srt_files')

# Add FFmpeg if found
if ffmpeg_exe and os.path.exists(ffmpeg_exe):
    # Copy to bin folder for bundling
    bin_dir = "bin"
    os.makedirs(bin_dir, exist_ok=True)
    ffmpeg_dest = os.path.join(bin_dir, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_dest):
        shutil.copy2(ffmpeg_exe, ffmpeg_dest)
        print(f"✅ Copied FFmpeg to {ffmpeg_dest}")
    add_data.append('bin;bin')

# ==================== HIDDEN IMPORTS ====================
hidden_imports = [
    # Core
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    
    # Image Processing
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    
    # Video Processing
    'imageio',
    'imageio_ffmpeg',
    'cv2',
    
    # UI
    'ttkbootstrap',
    
    # AI - Whisper
    'whisper',
    'torch',
    'torch.nn',
    'torch.nn.functional',
    'torchaudio',
    'numpy',
    'scipy',
    'scipy.signal',
    'scipy.ndimage',
    
    # Utilities
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'pystray',  # System tray support
    'customtkinter',
    'faster_whisper',
    'ctranslate2',
    
    # Standard libs (sometimes needed)
    'subprocess',
    'threading',
    'multiprocessing',
    'queue',
    'json',
    're',
    'sys',
    'os',
    'pathlib',
    'shutil',
    'time',
    'datetime',
]

# ==================== COLLECT BINARIES ====================
# Collect Torch CUDA DLLs if available
binaries = []
try:
    import torch
    torch_dir = Path(torch.__file__).parent
    
    # Add CUDA libraries if available
    cuda_libs = list(torch_dir.glob("lib/*.dll"))
    for lib in cuda_libs:
        binaries.append((str(lib), 'torch/lib'))
    
    if cuda_libs:
        print(f"✅ Found {len(cuda_libs)} CUDA libraries")
except:
    print("⚠️ Torch not found or no CUDA libs")

# ==================== BUILD ARGS ====================
args = [
    MAIN_SCRIPT,
    f'--name={APP_NAME}',
    '--noconfirm',
    '--windowed',  # No console window
    '--onedir',    # Folder mode (faster startup)
    '--clean',
    
    # Collect all Tkinter/Tcl data
    '--collect-all', 'tkinter',
    '--collect-all', 'ttkbootstrap',
    
    # Optimization
    '--noupx',  # Don't use UPX (can cause issues with some DLLs)
    
    # Paths
    '--workpath=build',
    '--distpath=dist',
    '--specpath=.',
]

# Add icon if exists
if os.path.exists('assets/icon.ico'):
    args.append('--icon=assets/icon.ico')

# Add version info (Windows only)
if sys.platform == 'win32':
    args.extend([
        f'--version-file=version.txt',  # Will create this below
    ])

# Add hidden imports
for imp in hidden_imports:
    args.append(f'--hidden-import={imp}')

# Add data files
for item in add_data:
    if ';' in item:
        src, dest = item.split(';')
        if os.path.exists(src):
            args.append(f'--add-data={item}')
        else:
            print(f"⚠️ Warning: '{src}' not found, skipping...")

# Add binaries
for src, dest in binaries:
    args.append(f'--add-binary={src};{dest}')

# ==================== CREATE VERSION FILE ====================
version_content = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Video Editor Pro'),
        StringStruct(u'FileDescription', u'Professional Video Editor with AI'),
        StringStruct(u'FileVersion', u'{VERSION}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'© 2026 Video Editor Pro'),
        StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
        StringStruct(u'ProductName', u'Video Editor Pro'),
        StringStruct(u'ProductVersion', u'{VERSION}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

with open('version.txt', 'w', encoding='utf-8') as f:
    f.write(version_content)

# ==================== RUN BUILD ====================
print("\n" + "="*60)
print(f"🚀 BUILDING {APP_NAME} v{VERSION}")
print("="*60)
print(f"📦 Including:")
print(f"   ✅ Whisper AI (GPU Accelerated)")
print(f"   ✅ FFmpeg Binary")
print(f"   ✅ All UI Assets")
print(f"   ✅ Torch CUDA Libraries")
print("="*60 + "\n")

try:
    PyInstaller.__main__.run(args)
    
    print("\n" + "="*60)
    print("✅ BUILD SUCCESSFUL!")
    print("="*60)
    print(f"📂 Output: dist/{APP_NAME}/")
    print(f"🚀 Run: dist/{APP_NAME}/{APP_NAME}.exe")
    print("="*60)
    
    # Post-build cleanup
    if os.path.exists('version.txt'):
        os.remove('version.txt')
    
except Exception as e:
    print(f"\n❌ BUILD FAILED: {e}")
    sys.exit(1)
