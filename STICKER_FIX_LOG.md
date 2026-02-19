# 🔧 Fix Log - Sticker + Blur Background Error

## Vấn Đề

Khi sử dụng **Blur Background** (chế độ Fit với blur) + **Sticker** cùng lúc, FFmpeg báo lỗi:
```
Invalid data found when processing input
Error parsing global options: Invalid data found when processing input
```

## Nguyên Nhân

1. **Filter Chain Conflict**: Khi blur background được bật, FFmpeg tạo một **complex filter** với cú pháp:
   ```
   split[bg][fg];[bg]...blur...[bg_blur];[fg]...scale...[fg_sized];[bg_blur][fg_sized]overlay=(W-w)/2:(H-h)/2
   ```

2. **Double Labeling**: Code cũ cố gắng thêm label `[v_main]` vào output của complex filter, nhưng complex filter đã có output riêng, gây ra conflict:
   ```
   [0:v]split[bg][fg];...overlay=(W-w)/2:(H-h)/2[v_main];  # ❌ SAI!
   ```

## Giải Pháp

### Thay Đổi Trong `utils/video_processor.py`

**Trước (Lỗi):**
```python
if vf:
    full_complex += f"[0:v]{vf}[v_main];"  # ❌ Không kiểm tra vf đã complex chưa
    bg_label = "[v_main]"
```

**Sau (Đúng):**
```python
# Check if we already have a complex filter
has_complex_filter = vf and (';' in vf or 'split[' in vf)

if has_complex_filter:
    # Blur background đã tạo complex filter, chỉ cần append sticker
    vf = f"{vf}[v_main];[1:v][v_main]scale2ref=...overlay=..."
elif vf:
    # Simple filter, convert to complex
    vf = f"[0:v]{vf}[v_main];[1:v][v_main]scale2ref=...overlay=..."
else:
    # No filter, just sticker
    vf = f"[1:v][0:v]scale2ref=...overlay=..."
```

### Logic Mới

1. **Detect Complex Filter**: Kiểm tra xem filter chain đã là complex chưa (có `;` hoặc `split[`)
2. **Smart Append**: 
   - Nếu đã complex → append trực tiếp với label
   - Nếu simple → convert sang complex
   - Nếu empty → tạo mới

## Test Cases

### ✅ Case 1: Simple Filter + Sticker
```
Input:  scale=iw*1.0:ih*1.0
Output: [0:v]scale=iw*1.0:ih*1.0[v_main];[1:v][v_main]scale2ref=w=iw*0.2:h=-1[stk][bg];[bg][stk]overlay=W-w-20:H-h-20
```

### ✅ Case 2: Blur Background + Sticker
```
Input:  split[bg][fg];[bg]scale=720:1280:...,boxblur=5.0:2.5[bg_blur];[fg]scale=720:1280:...[fg_sized];[bg_blur][fg_sized]overlay=(W-w)/2:(H-h)/2
Output: [same as input][v_main];[1:v][v_main]scale2ref=w=iw*0.2:h=-1[stk][bg];[bg][stk]overlay=W-w-20:H-h-20
```

### ✅ Case 3: No Filter + Sticker
```
Input:  None
Output: [1:v][0:v]scale2ref=w=iw*0.2:h=-1[stk][bg];[bg][stk]overlay=W-w-20:H-h-20
```

## Cách Sử Dụng

### Bật Blur Background + Sticker
1. Chọn **Aspect Ratio** khác "Giữ nguyên" (ví dụ: 9:16)
2. Chọn **Resize Mode** = "Thêm viền (Fit)"
3. Bật checkbox **"Làm mờ (Blur)"** và kéo slider
4. Chọn **Sticker** từ thư viện hoặc upload file
5. Chọn vị trí và kích thước sticker
6. Click **"XUẤT VIDEO"**

### Kết Quả
- ✅ Video được resize với blur background
- ✅ Sticker được overlay lên trên
- ✅ Không còn lỗi FFmpeg

## Các Lỗi Khác Đã Fix

### 1. Vietnamese Position Detection
**Thêm**: Hỗ trợ tên vị trí tiếng Việt
```python
if "Left" in s_pos or "trái" in s_pos: x_expr = "20"
if "Top" in s_pos or "trên" in s_pos: y_expr = "20"
if "Center" in s_pos or "giữa" in s_pos: x_expr = "(W-w)/2"; y_expr = "(H-h)/2"
```

## Lưu Ý

### ⚠️ Outro Concat Error
Lỗi concat outro vẫn còn (lỗi riêng, không liên quan đến sticker):
```
Nothing was written into output file, because at least one of its streams received no packets.
```

**Nguyên nhân**: Có thể do:
- File outro bị corrupt
- Codec không tương thích
- Audio/Video stream mismatch

**Giải pháp tạm thời**: Tắt outro hoặc dùng file outro khác

---

**Fixed by**: Nguyen Duy Duc  
**Date**: 2026-01-10  
**Version**: 1.0.1
