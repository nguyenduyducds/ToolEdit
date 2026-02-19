"""Script to split main.py into modular structure"""

import os
import re

def split_main_file():
    """Split main.py into separate modules"""
    
    # Read main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find class VideoEditorGUI
    class_start = content.find('class VideoEditorGUI:')
    class_end = content.find('\ndef main():')
    
    if class_start == -1 or class_end == -1:
        print("❌ Could not find class boundaries")
        return
    
    # Extract class content
    class_content = content[class_start:class_end]
    
    # Create main_window.py with proper imports
    main_window_content = '''"""Main window GUI for Video Editor Pro"""

import sys
import os
import uuid
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import time
import concurrent.futures
import multiprocessing
import subprocess
from datetime import datetime
import numpy as np
from scipy.ndimage import gaussian_filter
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import webbrowser
import json

# Try to import tkinterdnd2 for drag & drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False
    TkinterDnD = None

# Import from our modules
from config.settings import *
from core.ffmpeg_config import configure_ffmpeg, import_moviepy, setup_whisper, setup_speech_recognition
from core.update_checker import check_for_updates
from utils.helpers import detect_optimal_threads, get_video_files, GPU_ENCODE_SEMAPHORE

# Configure FFmpeg first
configure_ffmpeg()

# Import MoviePy
moviepy_modules = import_moviepy()
if moviepy_modules:
    VideoFileClip = moviepy_modules['VideoFileClip']
    concatenate_videoclips = moviepy_modules['concatenate_videoclips']
    AudioFileClip = moviepy_modules['AudioFileClip']
    TextClip = moviepy_modules['TextClip']
    CompositeVideoClip = moviepy_modules['CompositeVideoClip']
    ColorClip = moviepy_modules['ColorClip']
    ImageClip = moviepy_modules['ImageClip']
    vfx = moviepy_modules['vfx']
    afx = moviepy_modules['afx']
else:
    VideoFileClip = None
    concatenate_videoclips = None
    AudioFileClip = None
    TextClip = None
    CompositeVideoClip = None
    ColorClip = None
    ImageClip = None
    vfx = None
    afx = None

# Setup Whisper
whisper_config = setup_whisper()
WHISPER_AVAILABLE = whisper_config['available']
WHISPER_MODEL = whisper_config['model']
WHISPER_SEMAPHORE = whisper_config['semaphore']

# Setup Speech Recognition
sr_config = setup_speech_recognition()
SPEECH_RECOGNITION_AVAILABLE = sr_config['available']
sr = sr_config['module']


''' + class_content + '''
'''
    
    # Write to UI/main_window.py
    with open('UI/main_window.py', 'w', encoding='utf-8') as f:
        f.write(main_window_content)
    
    print("✅ Created UI/main_window.py")
    
    # Create new simplified main.py
    new_main_content = '''"""Video Editor Pro - Main Entry Point"""

import sys
import tkinter as tk

# Try to import tkinterdnd2 for drag & drop support
try:
    from tkinterdnd2 import TkinterDnD
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False
    TkinterDnD = None

# Import GUI
from UI.main_window import VideoEditorGUI


def main():
    """Main entry point"""
    # Use TkinterDnD if available for drag & drop support
    if TKDND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = VideoEditorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
'''
    
    # Backup original main.py
    if os.path.exists('main.py.backup'):
        print("⚠️ Backup already exists, skipping backup")
    else:
        os.rename('main.py', 'main.py.backup')
        print("✅ Backed up original main.py to main.py.backup")
    
    # Write new main.py
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_main_content)
    
    print("✅ Created new simplified main.py")
    print("\n📁 Structure created:")
    print("  ├── config/")
    print("  │   ├── __init__.py")
    print("  │   └── settings.py")
    print("  ├── core/")
    print("  │   ├── __init__.py")
    print("  │   ├── ffmpeg_config.py")
    print("  │   └── update_checker.py")
    print("  ├── utils/")
    print("  │   ├── __init__.py")
    print("  │   └── helpers.py")
    print("  ├── UI/")
    print("  │   ├── __init__.py")
    print("  │   └── main_window.py")
    print("  └── main.py (simplified)")


if __name__ == "__main__":
    split_main_file()
