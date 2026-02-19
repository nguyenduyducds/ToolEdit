# Auto-Cleanup Temporary SRT Files

## Problem
Temporary subtitle files (`temp_subs_*.srt`) were accumulating in the `srt_files` folder and not being deleted after use.

## Solution Implemented

### 1. **Auto-Delete After Processing**
Modified `UI/main_window.py` to automatically delete temporary SRT files after video processing completes:

```python
# Clean up temporary SRT file after processing
if srt_path and os.path.exists(srt_path):
    try:
        os.remove(srt_path)
        self.log(f"   🗑️ Cleaned up temp subtitle file")
    except Exception as e:
        self.log(f"   ⚠️ Could not delete temp SRT: {e}")
```

**When it runs:**
- After `process_video_with_ffmpeg()` completes
- For each video that had subtitles generated
- Logs the cleanup action

### 2. **Startup Cleanup**
Added `cleanup_old_srt_files()` method that runs when the app starts:

```python
def cleanup_old_srt_files(self):
    """Clean up old temporary SRT files from previous sessions"""
    try:
        srt_dir = "srt_files"
        if os.path.exists(srt_dir):
            srt_files = [f for f in os.listdir(srt_dir) 
                        if f.startswith("temp_subs_") and f.endswith(".srt")]
            if srt_files:
                for srt_file in srt_files:
                    try:
                        os.remove(os.path.join(srt_dir, srt_file))
                    except:
                        pass
                print(f"🗑️ Cleaned up {len(srt_files)} old subtitle file(s)")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
```

**When it runs:**
- On app startup (after config load)
- Cleans up leftover files from:
  - Previous crashes
  - Interrupted processing
  - Manual app termination

## Benefits

✅ **No manual cleanup needed** - Files deleted automatically
✅ **Prevents accumulation** - Folder stays clean
✅ **Handles crashes** - Startup cleanup removes orphaned files
✅ **Safe deletion** - Try/except prevents errors from blocking processing
✅ **User feedback** - Logs show when cleanup happens

## File Naming Pattern

Temporary files follow this pattern:
- `temp_subs_<thread_id>.srt`
- Example: `temp_subs_11376.srt`

Only files matching this pattern are deleted. Any manually created SRT files with different names are preserved.

## Testing

To verify:
1. Enable subtitles
2. Process a video
3. Check `srt_files` folder - should be empty after processing
4. Restart app - any leftover files should be cleaned up
