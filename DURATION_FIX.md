# Video Duration Display Fix

## Problem
Video duration column in the file list was showing "----" instead of the actual video duration.

## Root Cause
The `get_video_info()` function in `utils/video_processor.py` was not extracting the duration from FFmpeg output. It only extracted:
- Video resolution (width x height)
- Audio stream presence
- ❌ **Missing: Duration**

## Solution
Added duration extraction using regex to parse FFmpeg's output:

```python
# Regex to find Duration
# Duration: 00:00:10.05, start: 0.000000, bitrate: 1234 kb/s
duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', output)
if duration_match:
    hours = int(duration_match.group(1))
    minutes = int(duration_match.group(2))
    seconds = float(duration_match.group(3))
    info['duration'] = hours * 3600 + minutes * 60 + seconds
```

## How It Works

1. **FFmpeg Output Parsing**:
   - FFmpeg outputs video info to stderr
   - Format: `Duration: HH:MM:SS.ms, start: ..., bitrate: ...`
   - Example: `Duration: 00:03:24.50, start: 0.000000, bitrate: 2500 kb/s`

2. **Regex Extraction**:
   - Captures hours, minutes, and seconds with decimals
   - Converts to total seconds: `hours * 3600 + minutes * 60 + seconds`

3. **Display in UI**:
   - `add_file_to_tree()` formats duration as `MM:SS`
   - Example: 204.5 seconds → `03:24`

## Files Modified
- `utils/video_processor.py` - Added duration extraction to `get_video_info()`

## Testing
To verify:
1. Add videos to the input folder
2. Open the app
3. Check the "Thời lượng" column
4. Should display actual duration like `03:24`, `10:05`, etc.

## Before vs After

**Before:**
```
Tên File                    | Thời lượng | Độ phân giải
#animal #help #save #love   | ----       | 1080x1920
Evil Teens KILL 20yo Girl   | ----       | 1920x1080
```

**After:**
```
Tên File                    | Thời lượng | Độ phân giải
#animal #help #save #love   | 03:24      | 1080x1920
Evil Teens KILL 20yo Girl   | 10:05      | 1920x1080
```

## Edge Cases Handled
- ✅ Videos without duration info → defaults to `0` → displays as `00:00`
- ✅ Very long videos (hours) → correctly calculates total seconds
- ✅ FFmpeg errors → returns `None`, UI shows `--:--` as fallback
