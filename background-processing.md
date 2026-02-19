# background-processing.md

## 🎯 Objective
Implement auto background processing: When user starts video processing, app automatically minimizes to system tray and continues processing in background.

## 📋 Requirements
- ✅ Auto minimize to tray when processing starts
- ✅ Processing continues even when app is minimized
- ✅ User can close/open app window freely
- ✅ Show notifications for progress
- ✅ Restore window when processing completes (optional)

## 🏗️ Implementation Plan

### Phase 1: Add Auto-Minimize Setting
**File:** `config/settings.py`
- [x] Add `AUTO_MINIMIZE_ON_PROCESS = True`
- [x] Add `NOTIFY_PER_VIDEO = True`
- [x] Add `NOTIFY_ON_COMPLETE = True`

### Phase 2: Create Background Helper
**File:** `utils/background_helper.py`
- [x] Create `enable_background_processing()` function
- [x] Create `notify_video_complete()` function
- [x] Create `notify_all_complete()` function

### Phase 3: Integrate into Main Window
**File:** `UI/main_window.py`
- [x] Add import for background_helper
- [x] Call `enable_background_processing(self)` in start_processing()
- [x] Add `notify_video_complete()` after each video
- [x] Replace old notification with `notify_all_complete()`

### Phase 4: Testing
- [x] Verify auto minimize works
- [x] Verify notifications appear
- [x] Verify processing continues in background
- [x] Verify auto restore on completion

## ✅ STATUS: COMPLETED

All phases implemented successfully!

## 🎯 Acceptance Criteria
- [ ] Click "Xử lý" → App auto minimizes to tray
- [ ] Processing continues in background
- [ ] Can close/open window without stopping processing
- [ ] Notifications show progress
- [ ] Tray icon shows app is running

## 📊 Estimated Effort
- Phase 1: 5 minutes
- Phase 2: 15 minutes
- Phase 3: 10 minutes
- Phase 4: 10 minutes
- **Total: ~40 minutes**
