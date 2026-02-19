
import PyInstaller.__main__
import os
import sys
import shutil

# 1. Clean previous build
if os.path.exists("build"):
    try: shutil.rmtree("build") 
    except: pass
if os.path.exists("dist"):
    try: shutil.rmtree("dist")
    except: pass

# 2. Define Assets and Hidden Imports
# Helper to get site-packages path if needed
import site

# Manually robust data collection
datas = [
    ('assets', 'assets'),
    ('UI', 'UI'),
    ('utils', 'utils'),
    ('bin/ffmpeg.exe', '.'), # Put ffmpeg at root of internal bundle for easy access
    ('config', 'config'),
]

# Add Whisper Models if available
whisper_cache = os.path.join(os.path.expanduser('~'), '.cache', 'whisper')
if os.path.exists(whisper_cache):
    print(f"Found Whisper models at: {whisper_cache}")
    datas.append((whisper_cache, 'whisper_models'))
else:
    print("Warning: Whisper models not found in cache. App will download them on first run.")

# Hidden imports for dynamic modules
hidden_imports = [
    'PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL._tkinter_finder',
    'cv2', 'numpy', 
    'tkinter', 'tkinter.dnd', 'tkinter.ttk', 'tkinter.messagebox',
    'customtkinter', 
    'tkinterdnd2',
    'imageio', 'imageio_ffmpeg', 
    'requests', 'urllib3',
    'pystray',
    'babel', 'babel.numbers', # Common dependency for some UI libs
    'moviepy', # Just in case
    'proglog',
    'decorator',
    'tqdm',
    'anyio', 'attr', 'certifi'
]

# 3. PyInstaller Arguments
args = [
    'main.py',
    '--name=VideoEditorPro',
    '--noconfirm',
    '--clean',
    '--windowed',  # No Console
    '--onedir',    # Folder output (Faster startup than onefile)
    # '--icon=assets/icon.ico', # Uncomment if you have an icon
    
    # Paths
    '--paths=.',
    '--paths=UI',
    '--paths=utils',
]

# Add Datas
for src, dst in datas:
    if os.path.exists(src):
        args.append(f'--add-data={src}{os.pathsep}{dst}')

# Add Hidden Imports
for imp in hidden_imports:
    args.append(f'--hidden-import={imp}')

# Collect All hooks for complex packages
args.append('--collect-all=customtkinter')
args.append('--collect-all=tkinterdnd2')
args.append('--collect-all=moviepy')
args.append('--collect-all=imageio')
args.append('--collect-all=whisper') # If using local whisper

print("🚀 Starting Build Process...")
print(f"Args: {args}")

try:
    PyInstaller.__main__.run(args)
    print("\n✅ Build Successful! Output in 'dist/VideoEditorPro'")
except Exception as e:
    print(f"\n❌ Build Failed: {e}")
