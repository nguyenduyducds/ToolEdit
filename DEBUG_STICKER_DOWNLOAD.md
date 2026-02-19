# 🐛 DEBUG: Sticker Download Issue

## VẤN ĐỀ
Khi click vào sticker từ Giphy search, không tải về được.

## NGUYÊN NHÂN CÓ THỂ

### 1. Threading Issue
Download sticker chạy trong background thread nhưng UI update bị block.

### 2. Network Error
Giphy API rate limit hoặc URL không hợp lệ.

### 3. File Permission
Không thể ghi file vào `temp_stickers/`.

## CÁCH DEBUG

### Bước 1: Kiểm Tra Console
Khi click vào sticker, xem console có lỗi gì không:
- `Download Error: ...`
- `Giphy API Error: ...`
- Permission denied

### Bước 2: Kiểm Tra Thư Mục
```bash
# Check if temp_stickers folder exists
ls temp_stickers/

# Check permissions
# Windows: Right-click → Properties → Security
```

### Bước 3: Test Giphy API Manually
```python
# Test script
from utils.giphy_api import GiphyAPI

api = GiphyAPI()
results = api.search_stickers("hi", limit=5)
print(f"Found {len(results)} stickers")

if results:
    # Try download first one
    url = results[0]['full_url']
    sticker_id = results[0]['id']
    path = api.download_sticker(url, sticker_id)
    print(f"Downloaded to: {path}")
```

## QUICK FIX

Nếu vấn đề là threading, thêm error handling:

```python
# In main_window.py, find download_task function
def download_task():
    try:
        # ... existing code ...
        path = giphy_api.download_sticker(url, sticker_id)
        if path:
            print(f"✅ Downloaded: {path}")
            # Update UI
        else:
            print("❌ Download failed: No path returned")
    except Exception as e:
        print(f"❌ Download error: {e}")
        import traceback
        traceback.print_exc()
```

## TẠM THỜI: Dùng Local Stickers
Trong khi fix, bạn có thể:
1. Download stickers manually từ Giphy.com
2. Save vào `assets/stickers/`
3. Dùng local stickers thay vì online search

---

**Hãy chạy lại app và click vào sticker, rồi copy toàn bộ error message trong console cho tôi!**
