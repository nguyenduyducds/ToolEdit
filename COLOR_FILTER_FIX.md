# 🎨 Color Filter Fix - Invalid FFmpeg Filters

## ❌ Vấn Đề

FFmpeg báo lỗi khi sử dụng color filter "Lạnh lẽo (Cold)":
```
Failed to set value '...curves=blue_detect...' for option 'filter_complex': Invalid argument
```

## 🔍 Nguyên Nhân

Các filter **KHÔNG TỒN TẠI** trong FFmpeg:
- ❌ `curves=vintage` 
- ❌ `curves=blue_detect`

Đây là các preset của `curves` filter, nhưng FFmpeg không có sẵn các preset này (hoặc cần file LUT riêng).

## ✅ Giải Pháp

Thay thế bằng các filter **HỢP LỆ** và tạo hiệu ứng tương tự:

### 1. **Vintage (Phim Cũ)**
**Trước (SAI):**
```python
c_cmd = "curves=vintage"  # ❌ Không tồn tại
```

**Sau (ĐÚNG):**
```python
c_cmd = "eq=contrast=1.1:brightness=-0.05:saturation=0.8,colorbalance=rs=0.1:gs=-0.05:bs=-0.1"
```

**Hiệu ứng:**
- Tăng contrast nhẹ (1.1)
- Giảm độ sáng (-0.05)
- Giảm saturation (0.8) → màu nhạt hơn
- Thêm tông màu ấm (red +0.1, blue -0.1)

### 2. **Cold (Lạnh Lẽo)**
**Trước (SAI):**
```python
c_cmd = "curves=blue_detect"  # ❌ Không tồn tại
```

**Sau (ĐÚNG):**
```python
c_cmd = "colorbalance=rs=-0.2:gs=-0.1:bs=0.3,eq=saturation=1.2"
```

**Hiệu ứng:**
- Giảm red (-0.2) và green (-0.1)
- Tăng blue (+0.3) → tông màu lạnh
- Tăng saturation (1.2) → màu sắc rõ nét hơn

### 3. **Warm (Ấm Áp)**
**Cải thiện:**
```python
c_cmd = "colorbalance=rs=0.3:gs=-0.1:bs=-0.3,eq=saturation=1.1"
```

**Hiệu ứng:**
- Tăng red (+0.3)
- Giảm blue (-0.3) → tông màu ấm
- Tăng saturation nhẹ (1.1)

## 📊 Tất Cả Color Filters

| Filter | FFmpeg Command | Hiệu Ứng |
|--------|---------------|----------|
| **Gốc (None)** | *(không có)* | Giữ nguyên |
| **Đen Trắng (B&W)** | `hue=s=0` | Loại bỏ màu sắc |
| **Cổ điển (Sepia)** | `colorchannelmixer=.393:.769:...` | Tông màu nâu cổ điển |
| **Phim cũ (Vintage)** | `eq=contrast=1.1:...,colorbalance=...` | Giảm saturation + tông ấm |
| **Lạnh lẽo (Cold)** | `colorbalance=rs=-0.2:...,eq=saturation=1.2` | Tông xanh lạnh |
| **Ấm áp (Warm)** | `colorbalance=rs=0.3:...,eq=saturation=1.1` | Tông đỏ/vàng ấm |

## ✅ Validation

Tất cả filters đã được test với FFmpeg:

```bash
ffmpeg -f lavfi -i color=c=blue:s=320x240:d=1 -vf "FILTER_HERE" -f null -
```

**Kết quả:**
- ✅ Black & White: VALID
- ✅ Sepia: VALID
- ✅ Vintage: VALID
- ✅ Cold: VALID
- ✅ Warm: VALID

## 🎯 Cách Sử Dụng

1. Mở app
2. Tab **"Hình ảnh"**
3. Tìm dropdown **"Bộ lọc màu (Filter)"**
4. Chọn filter:
   - Đen Trắng (B&W)
   - Cổ điển (Sepia)
   - Ấm áp (Warm)
   - Lạnh lẽo (Cold)
   - Phim cũ (Vintage)
5. Render video

**Kết quả:** ✅ Video có color grading đẹp mắt!

## 🔧 Technical Details

### FFmpeg Filter Modules Used
- `hue`: Điều chỉnh hue/saturation
- `colorchannelmixer`: Mix các kênh màu (RGB)
- `colorbalance`: Điều chỉnh cân bằng màu (shadows/midtones/highlights)
- `eq`: Equalizer (brightness, contrast, saturation, gamma)

### Filter Chain Example
```
[0:v]scale=iw*1.0:ih*2.5,colorbalance=rs=-0.2:gs=-0.1:bs=0.3,eq=saturation=1.2[pre];
[pre]split[bg][fg];
...
```

## 📝 Code Changes

**File:** `utils/video_processor.py`  
**Lines:** 91-109  
**Changes:**
- Removed invalid `curves=vintage` and `curves=blue_detect`
- Added proper `colorbalance` + `eq` combinations
- Added Vietnamese keyword support

---

**Fixed by:** Nguyen Duy Duc  
**Date:** 2026-01-10  
**Version:** 1.0.3  
**Status:** ✅ **PRODUCTION READY**
