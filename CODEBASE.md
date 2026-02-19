# 📦 CODEBASE.md - File Dependencies Map

> **Purpose:** Track file dependencies to prevent breaking changes  
> **Rule:** Before editing ANY file, check this map first!

---

## 🗺️ FILE DEPENDENCY MAP

### 🚀 Entry Point

#### `main.py`
**Purpose:** Application entry point  
**Dependencies:**
- ✅ Imports: `UI/main_window.py`
- ✅ Imports: `tkinter`, `customtkinter`, `tkinterdnd2`
- ⚠️ **CRITICAL:** Changes here affect app startup

**Imported By:** NONE (entry point)

**Safe to Edit?** ⚠️ **CAUTION** - Only for startup logic

---

### ⚙️ Configuration Layer

#### `config/settings.py`
**Purpose:** Global constants and default settings  
**Dependencies:** NONE (pure constants)

**Imported By:**
- `UI/main_window.py`
- `core/ffmpeg_config.py`
- `core/update_checker.py`
- `utils/helpers.py`

**Safe to Edit?** ⚠️ **CAUTION** - Changes affect ENTIRE app

**Common Changes:**
- ✅ Add new constants
- ✅ Update default values
- ❌ Don't rename existing constants (breaks imports)

---

### 🔧 Core Layer

#### `core/ffmpeg_config.py`
**Purpose:** FFmpeg setup, MoviePy import, Whisper setup  
**Dependencies:**
- ✅ Imports: `config/settings.py`
- ✅ External: `moviepy`, `whisper`, `imageio_ffmpeg`

**Imported By:**
- `UI/main_window.py`
- `utils/video_processor.py`
- `utils/subtitle_generator.py`

**Safe to Edit?** ⚠️ **CAUTION** - Changes affect video processing

**Common Changes:**
- ✅ Update FFmpeg path detection
- ✅ Add new codec support
- ❌ Don't change function signatures (breaks callers)

---

#### `core/update_checker.py`
**Purpose:** Check for new app versions  
**Dependencies:**
- ✅ Imports: `config/settings.py`
- ✅ External: `requests`

**Imported By:**
- `UI/main_window.py`

**Safe to Edit?** ✅ **SAFE** - Isolated functionality

---

### 🛠️ Utils Layer (Pure Functions)

#### `utils/helpers.py`
**Purpose:** System utilities (threads, GPU detection)  
**Dependencies:**
- ✅ Imports: `config/settings.py`
- ✅ External: `psutil`, `threading`

**Imported By:**
- `UI/main_window.py`
- `utils/video_processor.py`

**Safe to Edit?** ⚠️ **CAUTION** - Used by multiple modules

**Common Changes:**
- ✅ Add new helper functions
- ✅ Optimize thread detection
- ❌ Don't change existing function signatures

---

#### `utils/video_processor.py`
**Purpose:** Video processing logic (FFmpeg commands)  
**Dependencies:**
- ✅ Imports: `core/ffmpeg_config.py`
- ✅ Imports: `utils/helpers.py`
- ✅ External: `moviepy`, `subprocess`, `numpy`

**Imported By:**
- `UI/main_window.py`

**Safe to Edit?** ✅ **SAFE** - Pure functions, single caller

**Common Changes:**
- ✅ Add new video effects
- ✅ Optimize FFmpeg commands
- ⚠️ Test thoroughly after changes

---

#### `utils/subtitle_generator.py`
**Purpose:** Subtitle generation (Whisper AI, Google Speech)  
**Dependencies:**
- ✅ Imports: `core/ffmpeg_config.py`
- ✅ External: `whisper`, `speech_recognition`, `moviepy`

**Imported By:**
- `UI/main_window.py`

**Safe to Edit?** ✅ **SAFE** - Pure functions, single caller

**Common Changes:**
- ✅ Add new subtitle engines
- ✅ Improve accuracy
- ⚠️ Test with different languages

---

### 🎨 UI Layer

#### `UI/main_window.py`
**Purpose:** Main GUI class (VideoEditorGUI)  
**Dependencies:**
- ✅ Imports: `config/settings.py`
- ✅ Imports: `core/ffmpeg_config.py`
- ✅ Imports: `core/update_checker.py`
- ✅ Imports: `utils/helpers.py`
- ✅ Imports: `utils/video_processor.py`
- ✅ Imports: `utils/subtitle_generator.py`
- ✅ Imports: `UI/effects_preview.py`
- ✅ Imports: `UI/preview_player.py`
- ✅ Imports: `UI/sticker.py`
- ✅ Imports: `UI/modules/config_manager.py`
- ✅ External: `tkinter`, `customtkinter`, `tkinterdnd2`, `PIL`

**Imported By:**
- `main.py`

**Safe to Edit?** ⚠️ **COMPLEX** - Huge file (164KB), many dependencies

**Common Changes:**
- ✅ Add new UI components
- ✅ Fix UI bugs
- ⚠️ **REFACTOR RECOMMENDED** - Split into smaller modules

**Refactoring Plan:**
```
UI/main_window.py (164KB) → Split into:
  ├── UI/components/video_list.py
  ├── UI/components/settings_panel.py
  ├── UI/components/console_panel.py
  ├── UI/components/toolbar.py
  └── UI/main_window.py (coordinator only)
```

---

#### `UI/effects_preview.py`
**Purpose:** Effects preview window  
**Dependencies:**
- ✅ External: `tkinter`, `customtkinter`, `PIL`

**Imported By:**
- `UI/main_window.py`

**Safe to Edit?** ✅ **SAFE** - Isolated UI component

---

#### `UI/preview_player.py`
**Purpose:** Video preview player  
**Dependencies:**
- ✅ External: `tkinter`, `PIL`, `cv2`

**Imported By:**
- `UI/main_window.py`

**Safe to Edit?** ✅ **SAFE** - Isolated UI component

---

#### `UI/sticker.py`
**Purpose:** Sticker management (Giphy integration)  
**Dependencies:**
- ✅ External: `tkinter`, `customtkinter`, `requests`, `PIL`

**Imported By:**
- `UI/main_window.py`

**Safe to Edit?** ✅ **SAFE** - Isolated UI component

---

#### `UI/modules/config_manager.py`
**Purpose:** Configuration UI and persistence  
**Dependencies:**
- ✅ Imports: `UI/modules/theme_manager.py`
- ✅ External: `json`, `tkinter`

**Imported By:**
- `UI/main_window.py`

**Safe to Edit?** ✅ **SAFE** - Isolated module

---

#### `UI/modules/theme_manager.py`
**Purpose:** Theme switching (Dark/Light mode)  
**Dependencies:**
- ✅ External: `customtkinter`

**Imported By:**
- `UI/modules/config_manager.py`
- `UI/main_window.py`

**Safe to Edit?** ✅ **SAFE** - Isolated module

---

## 🔴 CRITICAL EDITING RULES

### Rule 1: Check Dependencies First
```
BEFORE editing ANY file:
  1. Read this CODEBASE.md
  2. Find "Imported By" section
  3. If multiple importers → Test ALL of them
  4. If zero importers → Safe to refactor
```

### Rule 2: Function Signature Changes
```
IF changing function signature:
  1. Find all callers (use grep_search)
  2. Update ALL callers in same commit
  3. Test each caller individually
```

### Rule 3: Constant Renaming
```
IF renaming constant in config/settings.py:
  1. Search entire codebase for old name
  2. Update ALL references
  3. Run app and test all features
```

### Rule 4: Adding New Dependencies
```
IF adding new import:
  1. Add to requirements.txt
  2. Document in ARCHITECTURE.md
  3. Update this CODEBASE.md
```

---

## 📊 DEPENDENCY GRAPH (Visual)

```
main.py
  └─→ UI/main_window.py
      ├─→ config/settings.py
      ├─→ core/ffmpeg_config.py
      │   └─→ config/settings.py
      ├─→ core/update_checker.py
      │   └─→ config/settings.py
      ├─→ utils/helpers.py
      │   └─→ config/settings.py
      ├─→ utils/video_processor.py
      │   ├─→ core/ffmpeg_config.py
      │   └─→ utils/helpers.py
      ├─→ utils/subtitle_generator.py
      │   └─→ core/ffmpeg_config.py
      ├─→ UI/effects_preview.py
      ├─→ UI/preview_player.py
      ├─→ UI/sticker.py
      └─→ UI/modules/config_manager.py
          └─→ UI/modules/theme_manager.py
```

---

## 🎯 SAFE EDITING ZONES

### ✅ GREEN (Safe to Edit)
- `utils/video_processor.py` - Pure functions
- `utils/subtitle_generator.py` - Pure functions
- `UI/effects_preview.py` - Isolated component
- `UI/preview_player.py` - Isolated component
- `UI/sticker.py` - Isolated component
- `UI/modules/theme_manager.py` - Isolated module
- `core/update_checker.py` - Isolated functionality

### ⚠️ YELLOW (Caution Required)
- `utils/helpers.py` - Multiple importers
- `core/ffmpeg_config.py` - Critical for video processing
- `UI/modules/config_manager.py` - Affects settings persistence

### 🔴 RED (High Risk)
- `config/settings.py` - Imported by EVERYTHING
- `UI/main_window.py` - Huge file, many dependencies
- `main.py` - Entry point

---

## 🧪 TESTING CHECKLIST

### After Editing GREEN Zone
- [ ] Test the specific feature
- [ ] Run lint_runner.py

### After Editing YELLOW Zone
- [ ] Test all features that use this module
- [ ] Check all importers
- [ ] Run lint_runner.py
- [ ] Manual integration test

### After Editing RED Zone
- [ ] Test ENTIRE application
- [ ] Test all features one by one
- [ ] Run lint_runner.py
- [ ] Run security_scan.py
- [ ] Test on clean environment

---

**🎯 Always consult this file before making changes!**
