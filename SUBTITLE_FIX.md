# Subtitle Language Auto-Detection Fix

## Problem
User reported that long videos ("video dài") were not getting subtitles. The issue was:

1. **No language parameter was being passed to Whisper** - it defaulted to English ('en')
2. **Vietnamese videos processed as English** resulted in no recognized speech
3. **Empty segments list** caused the function to return `None` without creating subtitles
4. **No helpful error messages** to explain why subtitles failed

## Solution Implemented

### 1. **Auto-Detect Language (Default)**
- Added `subtitle_language` variable with default value `"auto (Tự động)"`
- When "auto" is selected, Whisper automatically detects the video's language
- This works for Vietnamese, English, Japanese, Korean, Chinese, and many other languages

### 2. **Language Selection Dropdown**
Added a language dropdown in the subtitle settings with options:
- **auto (Tự động)** - Automatic detection (DEFAULT)
- vi (Tiếng Việt) - Vietnamese
- en (English) - English
- ja (日本語) - Japanese
- ko (한국어) - Korean
- zh (中文) - Chinese

### 3. **Updated Whisper Integration**
Modified `generate_subtitles_with_whisper()` to:
- Accept `language=None` for auto-detection
- Only pass language parameter if user explicitly selects one
- Show detected language in logs

### 4. **Better Error Messages**
Added detailed logging when subtitles fail:
- Shows detected language vs selected language
- Warns about language mismatch
- Suggests using auto-detect mode
- Explains possible reasons (no audio, poor quality, background noise)

## How It Works Now

1. **User enables subtitles** - Language is set to "Auto-detect" by default
2. **Whisper processes audio** - Automatically identifies the language
3. **Generates subtitles** - Creates SRT file with proper timing
4. **Shows detected language** - Logs show what language was detected
5. **If fails** - Detailed error messages explain why

## Benefits

✅ **Works for all languages** - No need to manually select language
✅ **Better for long videos** - Proper language detection prevents empty results
✅ **Helpful error messages** - Users know why subtitles failed
✅ **Flexible** - Can still force specific language if needed

## Testing

To test:
1. Enable subtitles in the app
2. Leave language as "Auto-detect"
3. Process a Vietnamese video
4. Check logs - should show "Detected language: vi"
5. Subtitles should be generated successfully

## Files Modified

1. `UI/main_window.py`:
   - Added `subtitle_language` variable
   - Added language dropdown UI
   - Updated subtitle generation to pass language parameter

2. `utils/subtitle_generator.py`:
   - Updated `generate_subtitles_with_whisper()` to handle `language=None`
   - Added better error messages
   - Shows detected vs selected language
