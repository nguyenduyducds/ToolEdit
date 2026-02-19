# 🎛️ Tính Năng Quản Lý Cấu Hình - Video Editor Pro

## 📋 Tổng Quan

Đã thêm 3 tính năng mới để quản lý cấu hình trong tab **Cấu hình**:

### ✨ Các Tính Năng Mới

#### 1. 🔄 **RESET VỀ MẶC ĐỊNH**
- **Màu**: Vàng/Cam (Warning)
- **Chức năng**: Đặt lại TẤT CẢ cấu hình về giá trị mặc định
- **Bao gồm**:
  - Video settings (blur, brightness, zoom, speed, etc.)
  - Audio settings (volume, bass, treble)
  - Subtitle settings
  - Intro/Outro paths
  - Stickers
  - System settings (threads, GPU)
- **Xác nhận**: Hiển thị hộp thoại xác nhận trước khi reset

#### 2. 💾 **LƯU CẤU HÌNH**
- **Màu**: Xanh lá (Success)
- **Chức năng**: Lưu tất cả cấu hình hiện tại vào file JSON
- **Định dạng**: JSON với encoding UTF-8
- **Tên file mặc định**: `video_editor_config.json`
- **Nội dung lưu**:
  ```json
  {
    "version": "2.0.0",
    "video": { ... },
    "audio": { ... },
    "subtitle": { ... },
    "intro_outro": { ... },
    "stickers": { ... },
    "system": { ... }
  }
  ```

#### 3. 📂 **TẢI CẤU HÌNH**
- **Màu**: Xanh dương/Cyan (Accent)
- **Chức năng**: Tải cấu hình từ file JSON đã lưu
- **Tự động áp dụng**: Tất cả settings được áp dụng ngay lập tức
- **Cập nhật UI**: Tự động cập nhật giao diện (labels, sticker list, etc.)

## 🎨 Giao Diện

Các nút được thiết kế theo phong cách CapCut:
- **Layout**: 3 nút ngang, chiều rộng bằng nhau
- **Màu sắc**: Phân biệt rõ ràng theo chức năng
- **Icons**: Emoji trực quan (🔄, 💾, 📂)
- **Hover effect**: Sáng lên khi di chuột qua
- **Info text**: Hướng dẫn ngắn gọn bên dưới

## 📝 Cách Sử Dụng

### Lưu Cấu Hình Yêu Thích
1. Điều chỉnh tất cả settings theo ý muốn
2. Nhấn nút **💾 LƯU CẤU HÌNH**
3. Chọn vị trí và tên file (mặc định: `video_editor_config.json`)
4. Nhấn **Save**

### Tải Lại Cấu Hình
1. Nhấn nút **📂 TẢI CẤU HÌNH**
2. Chọn file JSON đã lưu trước đó
3. Nhấn **Open**
4. Tất cả settings được áp dụng tự động

### Reset Về Mặc Định
1. Nhấn nút **🔄 RESET VỀ MẶC ĐỊNH**
2. Xác nhận trong hộp thoại
3. Tất cả settings quay về giá trị ban đầu

## 💡 Use Cases

### 1. **Preset cho các loại video khác nhau**
- Lưu preset cho video YouTube (9:16, blur background, subtitles)
- Lưu preset cho video TikTok (fast speed, color filter)
- Lưu preset cho video chuyên nghiệp (original ratio, no effects)

### 2. **Backup cấu hình**
- Lưu cấu hình hiện tại trước khi thử nghiệm
- Dễ dàng quay lại nếu không hài lòng

### 3. **Chia sẻ settings**
- Export file JSON để chia sẻ với người khác
- Import settings từ đồng nghiệp/bạn bè

### 4. **Workflow nhanh**
- Không cần điều chỉnh lại từng setting mỗi lần
- Chỉ cần load preset phù hợp

## 🔧 Chi Tiết Kỹ Thuật

### File Structure
```
ToolEdit/
├── UI/
│   └── main_window.py  # Chứa 3 methods mới:
│                       # - reset_config()
│                       # - save_config()
│                       # - load_config()
└── config/
    └── settings.py     # Chứa các giá trị DEFAULT_*
```

### Methods Mới

#### `reset_config(self)`
- Đặt lại tất cả `tk.Variable` về giá trị mặc định từ `config/settings.py`
- Cập nhật UI labels (intro/outro file labels)
- Refresh sticker list
- Hiển thị thông báo thành công

#### `save_config(self)`
- Thu thập tất cả giá trị từ `tk.Variable`
- Tạo dictionary có cấu trúc rõ ràng
- Lưu vào file JSON với `indent=4` và `ensure_ascii=False`
- Hiển thị thông báo với tên file

#### `load_config(self)`
- Đọc file JSON
- Áp dụng từng nhóm settings với giá trị mặc định nếu thiếu
- Cập nhật UI tương ứng
- Hiển thị thông báo thành công

### Error Handling
- Tất cả methods đều có `try-except` block
- Hiển thị messagebox lỗi chi tiết nếu có vấn đề
- Log vào console để debug

## 🎯 Lợi Ích

✅ **Tiết kiệm thời gian**: Không cần điều chỉnh lại settings mỗi lần  
✅ **Tránh sai sót**: Sử dụng preset đã test kỹ  
✅ **Linh hoạt**: Dễ dàng chuyển đổi giữa các workflow khác nhau  
✅ **Chuyên nghiệp**: Quản lý cấu hình như các phần mềm pro  
✅ **Chia sẻ dễ dàng**: Export/Import settings qua file JSON  

## 📸 Screenshots

Xem ảnh minh họa trong artifacts để thấy giao diện mới!

---

**Phiên bản**: 2.0.0  
**Ngày cập nhật**: 2026-01-15  
**Tác giả**: Dev BÉ Đức Cute 💖
