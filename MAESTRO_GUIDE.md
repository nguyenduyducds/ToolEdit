# 🎓 MAESTRO_GUIDE.md - Hướng Dẫn Sử Dụng Maestro Cho ToolEdit

> **Mục đích:** Hướng dẫn cách sử dụng hệ thống Maestro AI để phát triển ToolEdit  
> **Đối tượng:** Developers, Contributors, AI Assistants

---

## 📚 MỤC LỤC

1. [Giới Thiệu Maestro](#giới-thiệu-maestro)
2. [Cách Hoạt Động](#cách-hoạt-động)
3. [Workflows Phổ Biến](#workflows-phổ-biến)
4. [Ví Dụ Thực Tế](#ví-dụ-thực-tế)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 GIỚI THIỆU MAESTRO

**Maestro v4.0** là hệ thống điều phối AI agents để phát triển phần mềm có hệ thống.

### Thành Phần Chính

```
.agent/
├── agents/        ← 16 chuyên gia (orchestrator, debugger, frontend-specialist...)
├── skills/        ← 41 kỹ năng (clean-code, python-patterns, testing...)
├── workflows/     ← 11 quy trình (plan, debug, deploy...)
└── rules/         ← Quy tắc toàn cục (GEMINI.md)
```

### Nguyên Tắc Hoạt Động

```
Request → Classify → Socratic Gate → Select Agent → Load Skills → Execute → Verify
```

---

## ⚙️ CÁCH HOẠT ĐỘNG

### 1️⃣ Request Classification

Mỗi yêu cầu được phân loại tự động:

| Loại Request | Ví Dụ | Agent | Cần PLAN.md? |
|--------------|-------|-------|--------------|
| **QUESTION** | "Làm sao để thêm effect?" | - | ❌ |
| **SIMPLE CODE** | "Fix bug theme toggle" | `debugger` | ❌ |
| **COMPLEX CODE** | "Thêm watermark động" | `orchestrator` → specialists | ✅ |
| **UI/UX** | "Redesign settings panel" | `frontend-specialist` | ✅ |
| **PERFORMANCE** | "Tối ưu tốc độ xử lý" | `performance-optimizer` | ✅ |

---

### 2️⃣ Socratic Gate (🛑 BẮT BUỘC)

**Trước khi code, AI sẽ hỏi tối thiểu 3 câu hỏi:**

```
User: "Thêm tính năng watermark"
  ↓
AI: 🛑 SOCRATIC GATE
  1. 🎯 Watermark type? (text/image/both)
  2. 📍 Position? (fixed/corner/moving)
  3. 🎨 Customization? (opacity/size/color/font)
  ↓
User: Trả lời...
  ↓
AI: ✅ Bắt đầu implementation
```

**Mục đích:** Tránh làm sai yêu cầu, tiết kiệm thời gian.

---

### 3️⃣ Agent Selection

Dựa trên request, AI chọn agent phù hợp:

```python
# Ví dụ: "Fix bug theme toggle"
Request Type: SIMPLE CODE (bug fix)
  ↓
Agent: debugger
  ↓
Skills: systematic-debugging, clean-code
  ↓
Action: 
  1. Read UI/modules/theme_manager.py
  2. Reproduce bug
  3. Find root cause (5 Whys)
  4. Fix bug
  5. Verify fix
  6. Run lint_runner.py
```

---

## 🚀 WORKFLOWS PHỔ BIẾN

### Workflow 1: Fix Bug

```bash
# Cách 1: Tự động
User: "Theme toggle không hoạt động"

# Cách 2: Dùng workflow
User: /debug
```

**Quy trình:**
1. **Reproduce** - Tái hiện bug
2. **Isolate** - Tìm component lỗi
3. **Understand** - Root cause analysis (5 Whys)
4. **Fix** - Sửa lỗi
5. **Verify** - Test lại
6. **Prevent** - Thêm test (nếu cần)

---

### Workflow 2: Add New Feature

```bash
User: /plan
User: "Thêm tính năng watermark động"
```

**Quy trình:**
1. **Socratic Gate** - Hỏi 3 câu về requirements
2. **Create Plan** - Tạo `{add-watermark}.md`
3. **Implementation** - Code theo plan
4. **Testing** - Viết tests
5. **Verification** - Chạy scripts

**Plan File Structure:**
```markdown
# add-watermark.md

## 🎯 Objective
Add dynamic watermark feature to videos

## 📋 Requirements
- Text watermark support
- Image watermark support
- Position: corner/center/moving
- Customization: opacity, size, color

## 🏗️ Implementation Plan
### Phase 1: Backend
- [ ] Add watermark logic to utils/video_processor.py
- [ ] Support text watermark
- [ ] Support image watermark

### Phase 2: Frontend
- [ ] Add watermark panel to UI/main_window.py
- [ ] Add position selector
- [ ] Add customization controls

### Phase 3: Testing
- [ ] Unit tests for watermark logic
- [ ] Manual UI testing

## ✅ Acceptance Criteria
- [ ] Text watermark works
- [ ] Image watermark works
- [ ] Position customizable
- [ ] No performance regression
```

---

### Workflow 3: Performance Optimization

```bash
User: /orchestrate
User: "Tối ưu tốc độ xử lý video"
```

**Quy trình:**
1. **Profile** - Đo performance hiện tại
2. **Identify** - Tìm bottlenecks
3. **Optimize** - Cải thiện (multiprocessing, GPU, caching)
4. **Measure** - Đo lại performance
5. **Verify** - Đảm bảo không break features

**Agents Involved:**
- `performance-optimizer` - Main agent
- `backend-specialist` - Code optimization
- `test-engineer` - Regression testing

---

### Workflow 4: Build & Deploy

```bash
User: /deploy
```

**Quy trình:**
1. **Pre-flight Checks**
   - [ ] Run `security_scan.py`
   - [ ] Run `lint_runner.py`
   - [ ] Run `test_runner.py`
   - [ ] Manual testing
2. **Build**
   - [ ] Run `build_final.py` or PyInstaller
   - [ ] Test .exe on clean machine
3. **Deploy**
   - [ ] Create release notes
   - [ ] Upload to distribution platform

---

## 💡 VÍ DỤ THỰC TẾ

### Ví Dụ 1: Fix Theme Toggle Bug

**User Request:**
```
"Theme toggle không hoạt động, khi click vẫn ở dark mode"
```

**AI Response:**
```markdown
## 🔍 Debugging: Theme Toggle Issue

### Phase 1: Reproduce
✅ Confirmed: Click theme toggle → No visual change

### Phase 2: Isolate
📍 File: UI/modules/theme_manager.py
📍 Function: toggle_theme()

### Phase 3: Root Cause (5 Whys)
WHY không đổi theme?
→ Because customtkinter.set_appearance_mode() not called

WHY không gọi?
→ Because toggle_theme() only updates variable, not applies

WHY không apply?
→ Because missing apply_theme() call

ROOT CAUSE: Missing theme application after toggle

### Phase 4: Fix
```python
# UI/modules/theme_manager.py
def toggle_theme(self):
    self.current_theme = "Light" if self.current_theme == "Dark" else "Dark"
    self.apply_theme()  # ← ADDED THIS LINE
```

### Phase 5: Verify
✅ Manual test: Theme toggle works
✅ Lint check: Passed
```

---

### Ví Dụ 2: Add Watermark Feature

**User Request:**
```
"Thêm tính năng watermark, cho phép thêm text hoặc logo vào video"
```

**AI Response (Socratic Gate):**
```markdown
## 🛑 Socratic Gate: Watermark Feature

Trước khi implement, tôi cần hiểu rõ requirements:

### 1. 🎯 Watermark Type
**Question:** Bạn muốn hỗ trợ loại watermark nào?

**Options:**
| Option | Pros | Cons | Use Case |
|--------|------|------|----------|
| Text only | Simple, fast | Limited branding | Personal videos |
| Image only | Professional | Needs logo file | Business videos |
| Both | Maximum flexibility | More complex UI | All use cases |

**If Not Specified:** I'll implement both (most flexible)

### 2. 📍 Position
**Question:** Watermark nên đặt ở đâu?

**Options:**
- Fixed corners (top-left, top-right, bottom-left, bottom-right)
- Center
- Moving (scrolling text)
- Custom coordinates

**If Not Specified:** Fixed corners + center

### 3. 🎨 Customization
**Question:** Người dùng có thể tùy chỉnh gì?

**Options:**
- Opacity (0-100%)
- Size (small/medium/large)
- Color (for text)
- Font (for text)

**If Not Specified:** Opacity + Size

---

**Please answer these questions so I can create the perfect implementation plan! 🎯**
```

**User Answers:**
```
1. Both (text + image)
2. Fixed corners + center
3. Opacity + Size + Color + Font
```

**AI Creates Plan:**
```markdown
# add-watermark.md

## 🎯 Objective
Add watermark feature supporting both text and image with full customization

## 📋 Requirements
- ✅ Text watermark with custom font, color, size
- ✅ Image watermark (logo)
- ✅ Position: 5 options (4 corners + center)
- ✅ Opacity control (0-100%)
- ✅ Size control (small/medium/large)

## 🏗️ Implementation Plan

### Phase 1: Backend (utils/video_processor.py)
**Agent:** backend-specialist  
**Tasks:**
- [ ] Add `add_text_watermark()` function
- [ ] Add `add_image_watermark()` function
- [ ] Support position calculation
- [ ] Support opacity/size scaling
- [ ] FFmpeg filter integration

### Phase 2: Frontend (UI/main_window.py)
**Agent:** frontend-specialist  
**Tasks:**
- [ ] Add "Watermark" tab in settings panel
- [ ] Add text input field
- [ ] Add image file picker
- [ ] Add position dropdown (5 options)
- [ ] Add opacity slider (0-100%)
- [ ] Add size dropdown (S/M/L)
- [ ] Add color picker (for text)
- [ ] Add font selector (for text)
- [ ] Add preview button

### Phase 3: Testing
**Agent:** test-engineer  
**Tasks:**
- [ ] Unit test: add_text_watermark()
- [ ] Unit test: add_image_watermark()
- [ ] Integration test: Full video processing with watermark
- [ ] Manual UI test: All controls work

### Phase 4: Documentation
- [ ] Update README.md
- [ ] Add watermark usage guide

## 🎯 Acceptance Criteria
- [ ] Text watermark renders correctly
- [ ] Image watermark renders correctly
- [ ] All 5 positions work
- [ ] Opacity control works (0-100%)
- [ ] Size control works (S/M/L)
- [ ] Color picker works (text)
- [ ] Font selector works (text)
- [ ] No performance regression
- [ ] All tests pass

## 📊 Estimated Effort
- Backend: 2-3 hours
- Frontend: 3-4 hours
- Testing: 1-2 hours
- **Total: 6-9 hours**
```

**Then AI implements step by step...**

---

## ✅ BEST PRACTICES

### 1. Always Read ARCHITECTURE.md First
```bash
# Trước khi bắt đầu session
AI: Reading ARCHITECTURE.md to understand project structure...
```

### 2. Check CODEBASE.md Before Editing
```bash
# Trước khi edit file
AI: Checking CODEBASE.md for dependencies...
AI: File UI/main_window.py is imported by main.py
AI: Safe to edit, but need to test main.py after changes
```

### 3. Use Socratic Gate for Complex Requests
```bash
# Nếu request phức tạp
AI: 🛑 SOCRATIC GATE - I need to ask 3 questions first...
```

### 4. Run Verification Scripts
```bash
# Sau khi code
AI: Running lint_runner.py...
AI: ✅ All checks passed!
```

### 5. Document Changes
```bash
# Sau khi implement
AI: Updating ARCHITECTURE.md with new watermark feature...
AI: Updating CODEBASE.md with new dependencies...
```

---

## 🐛 TROUBLESHOOTING

### Issue 1: AI Không Hỏi Socratic Gate

**Symptom:** AI bắt đầu code ngay mà không hỏi

**Solution:**
```bash
User: "STOP! Hãy hỏi tôi 3 câu hỏi trước khi code"
```

**Prevention:** Thêm vào request:
```bash
User: "Thêm watermark. Hãy hỏi tôi chi tiết trước khi implement."
```

---

### Issue 2: AI Sửa Sai File

**Symptom:** AI sửa file không liên quan

**Solution:**
```bash
User: "Hãy check CODEBASE.md trước khi sửa file"
```

**Prevention:** AI phải đọc CODEBASE.md trước khi edit

---

### Issue 3: Không Có Plan File

**Symptom:** AI code trực tiếp cho complex feature

**Solution:**
```bash
User: "/plan"
User: "Tạo plan file trước khi implement"
```

---

### Issue 4: Quên Chạy Tests

**Symptom:** Code xong nhưng không verify

**Solution:**
```bash
User: "Hãy chạy lint_runner.py và test_runner.py"
```

**Prevention:** Thêm vào workflow:
```bash
AI: ✅ Code complete
AI: Running verification scripts...
AI: - lint_runner.py: ✅ Passed
AI: - test_runner.py: ✅ Passed
```

---

## 🎓 LEARNING PATH

### Beginner (Week 1)
1. ✅ Đọc ARCHITECTURE.md
2. ✅ Đọc CODEBASE.md
3. ✅ Thử workflow `/debug` với bug đơn giản
4. ✅ Thử workflow `/plan` với feature nhỏ

### Intermediate (Week 2-3)
1. ✅ Sử dụng `/orchestrate` cho complex tasks
2. ✅ Tạo custom plan files
3. ✅ Chạy verification scripts
4. ✅ Refactor code với agents

### Advanced (Week 4+)
1. ✅ Tạo custom skills (nếu cần)
2. ✅ Tạo custom workflows
3. ✅ Optimize agent routing
4. ✅ Contribute back to Maestro system

---

## 📞 SUPPORT

### Tài Liệu Tham Khảo
- `ARCHITECTURE.md` - Kiến trúc tổng thể
- `CODEBASE.md` - File dependencies
- `.agent/rules/GEMINI.md` - Quy tắc toàn cục
- `.agent/agents/*.md` - Agent documentation
- `.agent/skills/*/SKILL.md` - Skill documentation

### Slash Commands
```bash
/plan          # Tạo plan cho feature mới
/debug         # Debug mode
/orchestrate   # Multi-agent coordination
/test          # Generate & run tests
/deploy        # Build & deploy
/status        # Check project status
```

---

**🎯 Maestro giúp bạn code nhanh hơn, ít bug hơn, và có hệ thống hơn!**
