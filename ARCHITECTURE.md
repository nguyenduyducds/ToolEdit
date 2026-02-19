# 🏗️ ARCHITECTURE.md - ToolEdit Video Editor Pro

> **Version:** 2.0.0  
> **Maestro Integration:** v4.0  
> **Last Updated:** 2026-01-17

---

## 📐 TỔNG QUAN KIẾN TRÚC

**ToolEdit** là một **Desktop Video Editor** được xây dựng bằng Python với:
- **Frontend:** CustomTkinter (Modern UI)
- **Backend:** FFmpeg + MoviePy + Whisper AI
- **Architecture:** Modular MVC-like pattern

---

## 🗂️ CẤU TRÚC DỰ ÁN

```
ToolEdit/
├── .agent/                    ← MAESTRO SYSTEM (16 agents, 41 skills, 11 workflows)
├── config/                    ← Configuration
│   └── settings.py           ← App constants, version, defaults
├── core/                      ← Core functionality
│   ├── ffmpeg_config.py      ← FFmpeg setup, MoviePy import
│   └── update_checker.py     ← Version checking
├── utils/                     ← Pure functions (NO UI dependencies)
│   ├── helpers.py            ← System helpers (threads, GPU)
│   ├── video_processor.py    ← Video processing logic
│   └── subtitle_generator.py ← Subtitle generation logic
├── UI/                        ← User Interface
│   ├── main_window.py        ← Main GUI class (164KB!)
│   ├── effects_preview.py    ← Effects preview
│   ├── preview_player.py     ← Video player
│   ├── sticker.py            ← Sticker management
│   └── modules/              ← UI modules
│       ├── config_manager.py ← Config UI
│       └── theme_manager.py  ← Theme switching
├── assets/                    ← Static assets
│   ├── themes/               ← CustomTkinter themes
│   ├── fonts/                ← Custom fonts
│   └── icons/                ← UI icons
├── main.py                    ← Entry point (92 lines)
└── requirements.txt           ← Python dependencies
```

---

## 🎭 AVAILABLE AGENTS (16)

| Agent | Domain | Use When |
|-------|--------|----------|
| `orchestrator` | Multi-agent coordination | Complex multi-domain tasks |
| `project-planner` | Planning & Architecture | New features, refactoring |
| `debugger` | Bug fixing | Crashes, errors, performance issues |
| `backend-specialist` | Backend logic | FFmpeg, video processing, API |
| `frontend-specialist` | UI/UX | CustomTkinter UI, themes, layouts |
| `mobile-developer` | Mobile apps | ❌ NOT APPLICABLE (Desktop app) |
| `security-auditor` | Security | File handling, user input validation |
| `test-engineer` | Testing | Unit tests, integration tests |
| `performance-optimizer` | Performance | Speed optimization, memory leaks |
| `database-architect` | Database | ❌ NOT APPLICABLE (No DB) |
| `devops-engineer` | Deployment | Build scripts, PyInstaller |
| `documentation-writer` | Documentation | README, guides, comments |
| `seo-specialist` | SEO | ❌ NOT APPLICABLE (Desktop app) |
| `game-developer` | Game dev | ❌ NOT APPLICABLE |
| `penetration-tester` | Security testing | Vulnerability testing |
| `explorer-agent` | Codebase discovery | Understanding code structure |

---

## 🛠️ AVAILABLE SKILLS (41)

### 🌐 Universal Skills (Always Active)
- `clean-code` ⭐ **MANDATORY** - Coding standards
- `brainstorming` - Socratic questioning
- `behavioral-modes` - Mode switching (plan/ask/edit)

### 🎨 UI/UX Skills
- `frontend-design` - Web UI patterns (⚠️ Adapt for Desktop)
- `ui-ux-pro-max` - Advanced UI/UX design

### 🔧 Backend Skills
- `python-patterns` - Python best practices
- `api-patterns` - API design (for future features)
- `performance-profiling` - Performance optimization

### 🧪 Testing Skills
- `testing-patterns` - Unit/Integration tests
- `tdd-workflow` - Test-driven development

### 🔒 Security Skills
- `vulnerability-scanner` - Security scanning
- `red-team-tactics` - Penetration testing

### 📝 Documentation Skills
- `documentation-templates` - README, guides
- `plan-writing` - {task-slug}.md format

### 🚀 DevOps Skills
- `deployment-procedures` - Build & deployment
- `powershell-windows` - Windows scripting
- `bash-linux` - Linux scripting (cross-platform)

### 🎮 Other Skills
- `systematic-debugging` - Root cause analysis
- `code-review-checklist` - Code review
- `lint-and-validate` - Linting & validation
- `i18n-localization` - Multi-language support

---

## 📜 AVAILABLE WORKFLOWS (11)

| Workflow | Command | Use Case |
|----------|---------|----------|
| Create App | `/create` | ❌ Not applicable (app exists) |
| Plan Feature | `/plan` | Plan new features |
| Orchestrate | `/orchestrate` | Complex multi-agent tasks |
| Debug | `/debug` | Systematic debugging |
| Test | `/test` | Generate & run tests |
| Deploy | `/deploy` | Build executable |
| Brainstorm | `/brainstorm` | Explore ideas |
| Enhance | `/enhance` | Add/update features |
| Status | `/status` | Check project status |
| Preview | `/preview` | ❌ Not applicable (no web server) |
| UI/UX Pro Max | `/ui-ux-pro-max` | UI redesign |

---

## 🔧 AVAILABLE SCRIPTS

### 📍 Location: `~/.gemini/antigravity/skills/<skill>/scripts/`

| Script | Skill | When to Use |
|--------|-------|-------------|
| `security_scan.py` | vulnerability-scanner | Before deploy, after file handling changes |
| `lint_runner.py` | lint-and-validate | Every code change |
| `test_runner.py` | testing-patterns | After logic change |
| `ux_audit.py` | frontend-design | After UI change |
| `accessibility_checker.py` | frontend-design | After UI change (adapt for desktop) |
| `bundle_analyzer.py` | performance-profiling | Before deploy (PyInstaller) |
| `dependency_analyzer.py` | vulnerability-scanner | Weekly / Before deploy |

---

## 🎯 PROJECT-SPECIFIC ROUTING

### Request Classification for ToolEdit

| Request Type | Example | Active Agent | Skills |
|--------------|---------|--------------|--------|
| **UI Change** | "Fix theme toggle", "Add button" | `frontend-specialist` | `frontend-design`, `clean-code` |
| **Video Processing** | "Add new effect", "Fix FFmpeg" | `backend-specialist` | `python-patterns`, `clean-code` |
| **Bug Fix** | "App crashes", "Memory leak" | `debugger` | `systematic-debugging`, `clean-code` |
| **Performance** | "Speed up processing", "Optimize" | `performance-optimizer` | `performance-profiling`, `python-patterns` |
| **Build/Deploy** | "Build .exe", "Create installer" | `devops-engineer` | `deployment-procedures`, `powershell-windows` |
| **New Feature** | "Add watermark", "Add intro/outro" | `orchestrator` → `project-planner` → specialists | Multiple |
| **Testing** | "Write tests", "Test coverage" | `test-engineer` | `testing-patterns`, `tdd-workflow` |
| **Security** | "Validate input", "Check vulnerabilities" | `security-auditor` | `vulnerability-scanner` |

---

## 📊 DEPENDENCY MAP

### Core Dependencies
```
main.py
  └─→ UI/main_window.py (VideoEditorGUI)
      ├─→ config/settings.py
      ├─→ core/ffmpeg_config.py
      ├─→ core/update_checker.py
      ├─→ utils/helpers.py
      ├─→ utils/video_processor.py
      ├─→ utils/subtitle_generator.py
      ├─→ UI/effects_preview.py
      ├─→ UI/preview_player.py
      ├─→ UI/sticker.py
      └─→ UI/modules/config_manager.py
          └─→ UI/modules/theme_manager.py
```

### External Dependencies
- **tkinter** - GUI framework
- **customtkinter** - Modern UI components
- **tkinterdnd2** - Drag & drop
- **moviepy** - Video editing
- **whisper** - AI subtitle generation
- **speech_recognition** - Google Speech API
- **imageio-ffmpeg** - FFmpeg binaries
- **pillow** - Image processing
- **numpy** - Numerical computing
- **psutil** - System utilities

---

## 🚀 WORKFLOW EXAMPLES

### Example 1: Fix UI Bug
```
User: "Theme toggle không hoạt động"
  ↓
CLASSIFY: SIMPLE CODE (single file fix)
  ↓
AGENT: debugger
  ↓
SKILLS: systematic-debugging, clean-code
  ↓
ACTION: 
  1. Read UI/modules/theme_manager.py
  2. Identify root cause
  3. Fix bug
  4. Verify fix
  5. Run lint_runner.py
```

### Example 2: Add New Feature
```
User: "Thêm tính năng watermark động"
  ↓
CLASSIFY: COMPLEX CODE (new feature)
  ↓
SOCRATIC GATE: Ask 3 questions
  - Watermark type? (text/image/both)
  - Position? (fixed/moving)
  - Customization? (opacity/size/color)
  ↓
AGENT: project-planner → Create {add-watermark}.md
  ↓
AGENT: backend-specialist → Implement in utils/video_processor.py
  ↓
AGENT: frontend-specialist → Add UI in UI/main_window.py
  ↓
AGENT: test-engineer → Write tests
  ↓
VERIFY: Run lint_runner.py, test_runner.py
```

### Example 3: Performance Optimization
```
User: "Tối ưu tốc độ xử lý video"
  ↓
CLASSIFY: COMPLEX CODE (performance)
  ↓
AGENT: performance-optimizer
  ↓
SKILLS: performance-profiling, python-patterns
  ↓
ACTION:
  1. Profile current performance
  2. Identify bottlenecks
  3. Optimize (multiprocessing, GPU, caching)
  4. Measure improvement
  5. Run bundle_analyzer.py
```

---

## 🔴 CRITICAL RULES FOR TOOLEDIT

### 1. File Modification Rules
```
BEFORE editing ANY file:
  1. Check ARCHITECTURE.md → Dependency Map
  2. Identify dependent files
  3. Update ALL affected files together
```

### 2. Agent Routing Rules
```
UI changes        → frontend-specialist ONLY
Video processing  → backend-specialist ONLY
Bug fixes         → debugger ONLY
New features      → orchestrator → project-planner → specialists
```

### 3. Testing Rules
```
AFTER every code change:
  1. Manual test in app
  2. Run lint_runner.py
  3. If logic change → Write unit test
  4. If UI change → Manual UX test
```

### 4. Build Rules
```
BEFORE building .exe:
  1. Run security_scan.py
  2. Run lint_runner.py
  3. Run test_runner.py
  4. Test app manually
  5. Build with PyInstaller
  6. Test .exe on clean machine
```

---

## 📝 NOTES

### Current State
- ✅ Well-structured modular architecture
- ✅ Pure functions separated from UI
- ✅ Good documentation (28 .md files)
- ⚠️ Main UI file is HUGE (164KB - needs refactoring)
- ⚠️ No unit tests yet
- ⚠️ No CI/CD pipeline

### Improvement Opportunities
1. **Refactor UI/main_window.py** - Split into smaller components
2. **Add Unit Tests** - Test utils/ functions
3. **Add Integration Tests** - Test video processing pipeline
4. **Performance Profiling** - Measure and optimize
5. **Security Audit** - Validate file inputs, prevent injection
6. **Build Automation** - CI/CD for .exe builds

---

**🎯 Use this file as the SINGLE SOURCE OF TRUTH for ToolEdit architecture.**
