# 🚀 Video Editor Pro - Build Guide

## 📋 Prerequisites

1. **Python 3.9-3.11** (Recommended: 3.10)
2. **NVIDIA GPU** (Optional, for GPU acceleration)
3. **CUDA Toolkit** (Optional, for GPU support)
4. **At least 10GB free disk space** (for build process)

## 🔧 Installation Steps

### Step 1: Install Dependencies

```bash
# Activate virtual environment (if using)
venv\Scripts\activate

# Install all dependencies
pip install -r requirements_full.txt
```

**For GPU Support (CUDA):**
```bash
# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 2: Build EXE

**Option A: Using Batch Script (Easiest)**
```bash
# Simply double-click or run:
build_full.bat
```

**Option B: Manual Build**
```bash
python build_full.py
```

## 📦 Build Output

After successful build, you'll find:
```
dist/
└── VideoEditorPro/
    ├── VideoEditorPro.exe  ← Main executable
    ├── assets/             ← UI resources
    ├── bin/
    │   └── ffmpeg.exe      ← Video processor
    ├── _internal/          ← Python runtime & libraries
    └── ... (other files)
```

## 🎯 Distribution

To distribute your app:
1. **Zip the entire `VideoEditorPro` folder**
2. Share the zip file
3. Users extract and run `VideoEditorPro.exe`

**No Python installation required on target computers!**

## ⚙️ Build Options

Edit `build_full.py` to customize:

- **App Name**: Change `APP_NAME = "VideoEditorPro"`
- **Version**: Change `VERSION = "2.0.0"`
- **Icon**: Place `icon.ico` in `assets/` folder
- **Console Window**: Remove `--windowed` to show console (for debugging)

## 🐛 Troubleshooting

### Build fails with "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements_full.txt --force-reinstall
```

### EXE is too large (>500MB)
This is normal! Includes:
- Python runtime (~50MB)
- Torch/CUDA libraries (~300MB)
- Whisper AI models (~100MB)
- FFmpeg (~50MB)

### GPU not working in EXE
Make sure CUDA DLLs are included:
- Check `dist/VideoEditorPro/_internal/torch/lib/` for `.dll` files
- If missing, install `torch` with CUDA before building

### FFmpeg not found
- The script auto-copies FFmpeg from `imageio_ffmpeg`
- If fails, manually copy `ffmpeg.exe` to `bin/` folder before building

## 📊 Build Time

Typical build times:
- **First build**: 10-15 minutes
- **Subsequent builds**: 5-8 minutes

## 🎉 Success Indicators

After build completes, test:
```bash
cd dist\VideoEditorPro
VideoEditorPro.exe
```

Should see:
- ✅ UI loads without errors
- ✅ Can import video files
- ✅ Whisper AI subtitle generation works
- ✅ Video export works with all filters

## 📝 Notes

- **Antivirus**: Some antivirus may flag the EXE as suspicious (false positive). Add exception if needed.
- **First Run**: May be slow (~30s) as it extracts temporary files.
- **Updates**: Rebuild EXE after code changes.

## 🆘 Support

If build fails, check:
1. Python version (3.9-3.11)
2. All dependencies installed
3. Enough disk space (10GB+)
4. No antivirus blocking PyInstaller

---
**Built with ❤️ using PyInstaller**
