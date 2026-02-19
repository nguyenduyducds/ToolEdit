# 📚 Sticker Library - Hướng Dẫn Sử Dụng

## Tổng Quan

Module Sticker/Watermark cho phép bạn thêm sticker, emoji, hoặc watermark lên video của mình, giống như CapCut!

## Tính Năng

### ✨ Thư Viện Sticker Có Sẵn
- **Emoji**: ❤️ Heart, ⭐ Star, 🔥 Fire, 👍 Thumbs Up, ⚡ Lightning
- **Watermark**: 📺 Subscribe, ▶️ Like & Subscribe, 🔔 Bell Icon
- **Custom**: Thêm sticker riêng của bạn

### 🎨 Tùy Chỉnh
- **5 vị trí**: Góc phải dưới, Góc phải trên, Góc trái dưới, Góc trái trên, Chính giữa
- **Kích thước linh hoạt**: 5% - 50% kích thước video
- **Hỗ trợ PNG với nền trong suốt**

## Cách Sử Dụng

### 1. Chọn Sticker Từ Thư Viện
1. Mở tab **"Sticker"** trong panel bên phải
2. Chọn danh mục (Emoji, Watermark, hoặc Custom)
3. Click vào sticker bạn muốn sử dụng
4. Sticker sẽ tự động được chọn và bật

### 2. Upload Sticker Riêng
1. Click nút **"Chọn File"** trong phần "Hoặc Tải File Riêng"
2. Chọn file ảnh PNG/JPG (khuyến nghị PNG với nền trong suốt)
3. File sẽ được sử dụng ngay lập tức

### 3. Điều Chỉnh Vị Trí & Kích Thước
1. Chọn vị trí từ dropdown menu
2. Kéo slider "Kích thước" để điều chỉnh size
3. Preview sẽ hiển thị ngay lập tức

## Thêm Sticker Mới Vào Thư Viện

### Cách 1: Thủ Công
1. Copy file PNG vào thư mục: `assets/stickers/`
2. Đặt tên file theo format: `tên_sticker.png` (ví dụ: `heart.png`, `logo.png`)
3. Restart ứng dụng

### Cách 2: Qua Code
```python
from UI.sticker import get_sticker_library

library = get_sticker_library()
library.add_custom_sticker("path/to/your/sticker.png", "My Custom Sticker")
```

## Kỹ Thuật

### Cấu Trúc Thư Mục
```
ToolEdit/
├── assets/
│   └── stickers/
│       ├── heart.png
│       ├── star.png
│       ├── fire.png
│       ├── thumbs.png
│       ├── lightning.png
│       └── subscribe.png
└── UI/
    └── sticker.py
```

### API Reference

#### StickerManager
- `apply_sticker_to_frame()`: Áp dụng sticker lên frame video
- `calculate_position()`: Tính toán vị trí sticker
- `resize_sticker()`: Thay đổi kích thước sticker
- `generate_ffmpeg_overlay_filter()`: Tạo FFmpeg filter string

#### StickerLibrary
- `get_sticker_path()`: Lấy đường dẫn sticker theo tên
- `get_all_stickers()`: Lấy danh sách tất cả sticker
- `add_custom_sticker()`: Thêm sticker tùy chỉnh

## Tips & Tricks

### 🎯 Sticker Đẹp
- Sử dụng PNG với nền trong suốt (alpha channel)
- Kích thước khuyến nghị: 512x512 hoặc 1024x1024 pixels
- Tránh file quá lớn (> 5MB) để tăng tốc độ xử lý

### ⚡ Hiệu Suất
- Sticker được cache tự động để tăng tốc
- FFmpeg xử lý overlay trực tiếp trên GPU (nếu có)
- Không ảnh hưởng đến tốc độ render

### 🎨 Thiết Kế
- **Góc phải dưới**: Phổ biến nhất cho watermark/logo
- **Chính giữa**: Phù hợp cho emoji reaction
- **Góc trái trên**: Tốt cho branding
- **Kích thước 15-20%**: Cân bằng giữa rõ ràng và không che khuất

## Ví Dụ

### Thêm Logo Watermark
```python
# Trong settings
settings = {
    'enable_sticker': True,
    'sticker_path': 'assets/stickers/subscribe.png',
    'sticker_pos': 'Góc phải dưới',
    'sticker_scale': 0.15  # 15% kích thước video
}
```

### Thêm Emoji Reaction
```python
settings = {
    'enable_sticker': True,
    'sticker_path': 'assets/stickers/fire.png',
    'sticker_pos': 'Chính giữa (Center)',
    'sticker_scale': 0.3  # 30% - lớn hơn để nổi bật
}
```

## Troubleshooting

### Sticker không hiển thị?
- ✅ Kiểm tra checkbox "Thêm Sticker/Logo" đã được bật
- ✅ Đảm bảo file sticker tồn tại
- ✅ Kiểm tra format file (PNG/JPG)

### Sticker bị mờ/vỡ?
- ✅ Sử dụng file có độ phân giải cao hơn
- ✅ Giảm scale nếu sticker quá nhỏ

### Không thấy sticker trong thư viện?
- ✅ Kiểm tra file đã được copy vào `assets/stickers/`
- ✅ Đặt tên file đúng format (lowercase, không dấu)
- ✅ Restart ứng dụng

## Roadmap

- [ ] Thêm nhiều sticker mặc định hơn
- [ ] Hỗ trợ GIF animated stickers
- [ ] Cho phép nhiều sticker cùng lúc
- [ ] Animation effects (fade in/out, bounce)
- [ ] Sticker marketplace/download

---

**Tạo bởi**: Nguyen Duy Duc  
**Version**: 1.0  
**Ngày**: 2026-01-10
