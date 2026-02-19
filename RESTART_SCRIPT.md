# Clean Restart Script

## Purpose
This script (`restart_clean.bat`) ensures the app runs with the latest code changes by:
1. Stopping any running instances
2. Cleaning Python cache
3. Removing temporary files
4. Starting the app fresh

## What It Does

### Step 1: Stop Running Instances
```batch
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Video Editor Pro*"
```
- Forcefully closes any running Python instances with "Video Editor Pro" in the title
- Ensures no conflicts with old processes

### Step 2: Clean Python Cache
```batch
rd /s /q "__pycache__"
rd /s /q "UI\__pycache__"
rd /s /q "UI\modules\__pycache__"
rd /s /q "utils\__pycache__"
rd /s /q "core\__pycache__"
```
- Removes all `__pycache__` directories
- Forces Python to recompile all modules
- Ensures latest code is loaded

### Step 3: Clean Temporary Files
```batch
del /q "*.pyc"
del /q "UI\*.pyc"
del /q "utils\*.pyc"
```
- Deletes compiled Python bytecode files
- Removes any stale `.pyc` files

### Step 4: Start App
```batch
python main.py
```
- Launches the app with fresh, recompiled code
- All changes are now active

## When to Use

Use this script when:
- ✅ You've made code changes and they don't appear
- ✅ UI elements aren't updating after edits
- ✅ Theme changes aren't applying
- ✅ Python is caching old modules
- ✅ You want to ensure a clean start

## How to Run

### Method 1: Double-click
1. Navigate to `ToolEdit` folder
2. Double-click `restart_clean.bat`
3. App will restart with clean cache

### Method 2: Command Line
```powershell
cd C:\Users\Admin\Desktop\ToolEdit\ToolEdit
.\restart_clean.bat
```

### Method 3: From VS Code Terminal
```powershell
.\restart_clean.bat
```

## What You'll See

```
========================================
  Video Editor Pro - Clean Restart
========================================

[1/4] Stopping any running instances...
[2/4] Cleaning Python cache...
   ✓ Cache cleared
[3/4] Cleaning temporary files...
   ✓ Temp files cleaned
[4/4] Starting Video Editor Pro...

[App launches]
```

## Benefits

✅ **Guaranteed Fresh Start** - No cached code
✅ **Fast** - Takes only 1-2 seconds
✅ **Safe** - Only removes cache, not data
✅ **Automatic** - One click does everything
✅ **Error Handling** - Shows errors if something fails

## Notes

- This script is safe to run anytime
- It won't delete your videos, configs, or settings
- Only removes Python cache and temp files
- If app is already running, it will be closed first
- All your data in `input/`, `output/`, and config files are preserved

## Alternative: Manual Cleanup

If you prefer manual cleanup:

1. Close the app
2. Delete `__pycache__` folders:
   - `ToolEdit\__pycache__`
   - `ToolEdit\UI\__pycache__`
   - `ToolEdit\utils\__pycache__`
3. Run `python main.py`
