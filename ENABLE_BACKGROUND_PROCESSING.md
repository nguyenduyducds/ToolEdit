# 🚀 HƯỚNG DẪN ENABLE BACKGROUND PROCESSING

## ✅ ĐÃ HOÀN THÀNH

### 1. Thêm Settings
✅ File: `config/settings.py`
```python
AUTO_MINIMIZE_ON_PROCESS = True  # Tự động minimize khi xử lý
NOTIFY_PER_VIDEO = True  # Thông báo mỗi video
NOTIFY_ON_COMPLETE = True  # Thông báo khi hoàn thành
```

### 2. Tạo Background Helper
✅ File: `utils/background_helper.py`
- `enable_background_processing()` - Auto minimize to tray
- `notify_video_complete()` - Notification per video
- `notify_all_complete()` - Notification when done

---

## 📝 CẦN BẠN LÀM (3 BƯỚC ĐƠN GIẢN)

### BƯỚC 1: Thêm Import
Mở file `UI/main_window.py`, tìm dòng ~32 (nơi có các import từ utils), thêm:

```python
# Dòng ~32, sau dòng:
# from utils.subtitle_generator import generate_subtitles_with_whisper, generate_subtitles_with_google

# THÊM DÒNG NÀY:
from utils.background_helper import enable_background_processing, notify_video_complete, notify_all_complete
```

---

### BƯỚC 2: Tìm Hàm `start_processing`
Trong file `UI/main_window.py`, tìm hàm `def start_processing(self):` 

**Cách tìm:**
- Nhấn `Ctrl+F` (hoặc `Cmd+F` trên Mac)
- Tìm: `def start_processing`
- Hoặc tìm: `XUẤT VIDEO` (vì button gọi hàm này)

---

### BƯỚC 3: Thêm 1 Dòng Code
Ngay sau dòng `def start_processing(self):`, thêm:

```python
def start_processing(self):
    """Start video processing"""
    # THÊM DÒNG NÀY (ngay sau docstring hoặc ngay đầu hàm):
    enable_background_processing(self)
    
    # ... code cũ tiếp tục ...
```

---

### BƯỚC 4 (OPTIONAL): Thêm Notifications
Tìm nơi xử lý từng video (vòng lặp for), thêm notification:

```python
# Sau khi xử lý xong 1 video, thêm:
notify_video_complete(self, video_name, current_index + 1, total_videos)

# Sau khi xử lý xong TẤT CẢ video, thêm:
notify_all_complete(self, total_processed)
```

---

## 🎯 KẾT QUẢ MONG ĐỢI

Sau khi hoàn thành:
1. ✅ Click "XUẤT VIDEO / BẮT ĐẦU"
2. ✅ App hiện message: "📱 App sẽ chạy ngầm..."
3. ✅ Sau 1.5 giây → App tự động minimize xuống System Tray
4. ✅ Icon xuất hiện bên cạnh đồng hồ Windows
5. ✅ Xử lý video tiếp tục chạy ngầm
6. ✅ Notification hiện mỗi khi xong 1 video
7. ✅ Notification "🎉 Hoàn thành!" khi xong tất cả
8. ✅ Click icon System Tray → App hiện lại

---

## 🐛 NẾU GẶP LỖI

### Lỗi: "pystray not installed"
```bash
pip install pystray pillow
```

### Lỗi: Không tìm thấy hàm `start_processing`
Hàm có thể có tên khác. Tìm button "XUẤT VIDEO" trong code:
```python
# Tìm dòng này:
command=self.start_processing
# Xem tên hàm thực sự là gì
```

### App không minimize
Kiểm tra:
1. `pystray` đã cài chưa?
2. `AUTO_MINIMIZE_ON_PROCESS = True` trong `config/settings.py`?
3. Có gọi `enable_background_processing(self)` chưa?

---

## 📞 CẦN TRỢ GIÚP?

Nếu bạn không tìm thấy hàm `start_processing`, hãy:
1. Copy 50 dòng code xung quanh button "XUẤT VIDEO / BẮT ĐẦU"
2. Gửi cho tôi
3. Tôi sẽ chỉ chính xác nơi cần thêm code

---

**🎯 Hoặc nếu muốn tôi làm hết, hãy cho tôi quyền edit file `UI/main_window.py`!**
