# Video Editor Pro - Cấu trúc dự án

## 📁 Cấu trúc thư mục

```
ToolEdit/
├── config/                 # Cấu hình ứng dụng
│   ├── __init__.py
│   └── settings.py        # Constants, settings, version info
│
├── core/                   # Chức năng cốt lõi
│   ├── __init__.py
│   ├── ffmpeg_config.py   # Cấu hình FFmpeg, import MoviePy
│   └── update_checker.py  # Kiểm tra cập nhật
│
├── utils/                  # Tiện ích
│   ├── __init__.py
│   └── helpers.py         # Hàm tiện ích (detect threads, get files, etc.)
│
├── UI/                     # Giao diện người dùng
│   ├── __init__.py
│   └── main_window.py     # Class VideoEditorGUI (toàn bộ GUI)
│
├── Model/                  # (Dự phòng cho tương lai)
│
├── main.py                 # Entry point chính (32 dòng)
├── main.py.backup         # Backup file gốc
└── requirements.txt       # Dependencies
```

## 🎯 Mô tả các module

### 1. `config/` - Cấu hình
- **settings.py**: Chứa tất cả constants, version, đường dẫn mặc định, settings mặc định

### 2. `core/` - Chức năng cốt lõi
- **ffmpeg_config.py**: 
  - Tìm và cấu hình FFmpeg
  - Import MoviePy
  - Setup Whisper
  - Setup Speech Recognition
  
- **update_checker.py**: 
  - Kiểm tra phiên bản mới từ server

### 3. `utils/` - Tiện ích
- **helpers.py**:
  - `detect_optimal_threads()`: Tự động phát hiện số luồng tối ưu
  - `get_video_files()`: Lấy danh sách video từ thư mục
  - `GPU_ENCODE_SEMAPHORE`: Semaphore cho GPU encoding

### 4. `UI/` - Giao diện
- **main_window.py**: 
  - Class `VideoEditorGUI` chính
  - Toàn bộ logic UI và xử lý video

### 5. `main.py` - Entry point
- File khởi động chính, rất gọn gàng (32 dòng)
- Import và khởi chạy GUI

## 🚀 Cách chạy

```bash
python main.py
```

## 📝 Lợi ích của cấu trúc mới

✅ **Dễ bảo trì**: Code được tách thành các module rõ ràng
✅ **Dễ mở rộng**: Thêm tính năng mới dễ dàng hơn
✅ **Dễ debug**: Tìm lỗi nhanh hơn khi biết code ở đâu
✅ **Dễ test**: Có thể test từng module riêng
✅ **Tái sử dụng**: Các hàm utility có thể dùng ở nhiều nơi
✅ **Clean code**: main.py chỉ 32 dòng thay vì 4091 dòng!

## 🔄 So sánh

### Trước:
- `main.py`: **4091 dòng** - Tất cả code trong 1 file

### Sau:
- `main.py`: **32 dòng** - Entry point gọn gàng
- `config/settings.py`: **41 dòng** - Cấu hình
- `core/ffmpeg_config.py`: **147 dòng** - FFmpeg setup
- `core/update_checker.py`: **31 dòng** - Update checker
- `utils/helpers.py`: **76 dòng** - Utilities
- `UI/main_window.py`: **~3900 dòng** - GUI logic

## 📌 Lưu ý

- File gốc đã được backup tại `main.py.backup`
- Nếu có lỗi, có thể khôi phục bằng cách:
  ```bash
  copy main.py.backup main.py
  ```

## 🎨 Tương lai

Có thể tách thêm `UI/main_window.py` thành các file nhỏ hơn:
- `UI/video_list_panel.py` - Quản lý danh sách video
- `UI/settings_panel.py` - Panel cài đặt
- `UI/console_panel.py` - Console log
- `utils/video_processor.py` - Xử lý video
- `utils/subtitle_generator.py` - Tạo subtitle

---

**Tác giả**: Nguyễn Duy Đức  
**Version**: 2.0.0
