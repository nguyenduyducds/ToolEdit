# 🎬 Video Editor Pro

**AI-Powered Video Editor with Automatic Subtitle Generation**

Version: 2.0.0 | Author: Nguyễn Duy Đức

---

## ✨ Tính năng

- 🎥 **Xử lý video tự động** với FFmpeg
- 🎤 **Tạo phụ đề tự động** bằng Whisper AI hoặc Google Speech Recognition
- 🎨 **Hiệu ứng chống bản quyền**: Blur, Brightness, Zoom, Speed, Mirror
- 📱 **Chuyển đổi Portrait** (9:16) cho mobile
- 🔥 **GPU Acceleration** (NVIDIA NVENC)
- 🚀 **Xử lý đa luồng** (tự động phát hiện cấu hình tối ưu)
- 🎬 **Intro/Outro** tùy chỉnh
- 💬 **Watermark** và nhiều hiệu ứng khác

---

## 📁 Cấu trúc dự án

```
ToolEdit/
├── .agent/          # 🤖 Maestro AI System (16 agents, 41 skills, 11 workflows)
├── config/          # Cấu hình
├── core/            # Chức năng cốt lõi (FFmpeg, Update)
├── utils/           # Tiện ích (Video, Subtitle, Helpers)
├── UI/              # Giao diện người dùng
├── main.py          # Entry point (92 dòng)
└── requirements.txt # Dependencies
```

📚 **Xem chi tiết**: 
- [STRUCTURE_DIAGRAM.md](STRUCTURE_DIAGRAM.md) - Sơ đồ cấu trúc
- [ARCHITECTURE.md](ARCHITECTURE.md) - Kiến trúc tổng thể
- [CODEBASE.md](CODEBASE.md) - File dependencies
- [MAESTRO_GUIDE.md](MAESTRO_GUIDE.md) - 🤖 Hướng dẫn Maestro AI

---

## 🤖 Maestro AI Development System

**ToolEdit** được phát triển với **Maestro v4.0** - Hệ thống điều phối AI agents chuyên nghiệp.

### Tính Năng Maestro

- 🎯 **16 AI Agents** - Chuyên gia cho từng domain (debugger, frontend, backend...)
- 🛠️ **41 Skills** - Kỹ năng chuyên môn (clean-code, python-patterns, testing...)
- 🚀 **11 Workflows** - Quy trình tự động (/plan, /debug, /deploy...)
- 🛑 **Socratic Gate** - Hỏi trước khi code, tránh sai yêu cầu
- ✅ **Auto Verification** - Tự động chạy lint, tests, security scan

### Slash Commands

```bash
/plan          # Tạo plan cho feature mới
/debug         # Debug mode (systematic root cause analysis)
/orchestrate   # Multi-agent coordination
/test          # Generate & run tests
/deploy        # Build & deploy executable
/status        # Check project status
```

### Ví Dụ Sử Dụng

```bash
# Fix bug
User: "Theme toggle không hoạt động"
AI: 🔍 Activating debugger agent...
AI: ✅ Root cause found: Missing apply_theme() call
AI: ✅ Fixed and verified

# Add feature
User: /plan
User: "Thêm watermark động"
AI: 🛑 SOCRATIC GATE - I need to ask 3 questions first...
AI: [Asks about type, position, customization]
User: [Answers...]
AI: ✅ Creating implementation plan: add-watermark.md
AI: ✅ Implementing with backend-specialist + frontend-specialist
AI: ✅ Running tests and verification
```

📚 **Xem hướng dẫn đầy đủ**: [MAESTRO_GUIDE.md](MAESTRO_GUIDE.md)

---

## 🚀 Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd ToolEdit
```

### 2. Tạo Virtual Environment (Khuyến nghị)
```bash
python -m venv venv
```

### 3. Kích hoạt Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

📚 **Xem chi tiết**: [VENV_GUIDE.md](VENV_GUIDE.md)

### 4. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 5. Chạy ứng dụng
```bash
python main.py
```

---

## 📦 Dependencies

- **tkinter** - GUI framework
- **tkinterdnd2** - Drag & drop support
- **moviepy** - Video editing
- **whisper** - AI subtitle generation
- **speech_recognition** - Google Speech Recognition
- **imageio-ffmpeg** - FFmpeg binaries
- **pillow** - Image processing
- **numpy** - Numerical computing
- **scipy** - Scientific computing
- **psutil** - System utilities
- **requests** - HTTP requests

---

## 🎯 Cách sử dụng

### 1. Thêm video
- Kéo thả video vào ô "Drop Zone"
- Hoặc click để chọn file

### 2. Cài đặt
- Chọn thư mục input/output
- Điều chỉnh hiệu ứng (blur, brightness, zoom, etc.)
- Bật/tắt subtitle tự động
- Chọn intro/outro (tùy chọn)

### 3. Xử lý
- Click "Xử lý tất cả" để bắt đầu
- Theo dõi tiến độ trong console
- Video đã xử lý sẽ nằm trong thư mục output/

---

## ⚙️ Cấu hình

### Tự động phát hiện cấu hình tối ưu:
- Số luồng xử lý (dựa trên RAM, CPU, GPU)
- GPU acceleration (NVIDIA NVENC)
- Whisper model size (dựa trên RAM)

### Tùy chỉnh:
- Chỉnh số luồng thủ công (1-32)
- Bật/tắt GPU rendering
- Chọn hiệu ứng anti-copyright
- Tùy chỉnh subtitle (font, color, outline)

---

## 📚 Tài liệu

- [STRUCTURE_DIAGRAM.md](STRUCTURE_DIAGRAM.md) - Sơ đồ cấu trúc dự án
- [README_STRUCTURE.md](README_STRUCTURE.md) - Giải thích chi tiết cấu trúc
- [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md) - Hướng dẫn tối ưu
- [FINAL_SUMMARY.md](FINAL_SUMMARY.md) - Tóm tắt refactor

---

## 🔧 Phát triển

### Cấu trúc code:

#### `config/` - Cấu hình
- `settings.py` - Constants, version, default settings

#### `core/` - Chức năng cốt lõi
- `ffmpeg_config.py` - FFmpeg setup, MoviePy import
- `update_checker.py` - Kiểm tra phiên bản mới

#### `utils/` - Tiện ích (Pure Functions)
- `helpers.py` - System helpers
- `video_processor.py` - Video processing logic
- `subtitle_generator.py` - Subtitle generation logic

#### `UI/` - Giao diện
- `main_window.py` - VideoEditorGUI class

---

## 🎨 Kiến trúc

### Entry Point
```python
# main.py (32 dòng)
from UI.main_window import VideoEditorGUI

def main():
    root = tk.Tk()
    app = VideoEditorGUI(root)
    root.mainloop()
```

### Pure Functions
```python
# utils/video_processor.py
def process_video_with_ffmpeg(input_path, output_path, settings):
    """Process video without UI dependencies"""
    ...

# utils/subtitle_generator.py
def generate_subtitles_with_whisper(audio_path, language):
    """Generate subtitles without UI dependencies"""
    ...
```

### UI Class
```python
# UI/main_window.py
class VideoEditorGUI:
    def process_video(self, filename):
        # Gọi pure functions
        srt = generate_subtitles_with_whisper(...)
        result = process_video_with_ffmpeg(...)
```

---

## 🐛 Debug

### Bật debug mode:
```python
# config/settings.py
DEBUG_MODE = True
```

### Xem logs:
- Console panel trong app
- Terminal output

---

## 📝 License

MIT License - Free to use and modify

---

## 👨‍💻 Tác giả

**Nguyễn Duy Đức**

---

## 🙏 Credits

- **FFmpeg** - Video processing
- **OpenAI Whisper** - AI subtitle generation
- **Google Speech Recognition** - Speech-to-text
- **MoviePy** - Python video editing
- **Tkinter** - GUI framework

---

## 📞 Liên hệ

- GitHub: [Your GitHub]
- Email: [Your Email]

---

**⭐ Nếu thấy hữu ích, hãy cho project một star!**
