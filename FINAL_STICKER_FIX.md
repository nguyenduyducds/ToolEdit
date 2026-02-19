# 🎯 FINAL FIX - Sticker + Blur Background + Scale

## ✅ Đã Fix Hoàn Toàn!

### 🐛 Vấn Đề Ban Đầu

Khi sử dụng **Scale Transform** + **Blur Background** + **Sticker** cùng lúc, FFmpeg báo lỗi:
```
Invalid data found when processing input
Error parsing global options: Invalid data found when processing input
```

### 🔍 Root Cause Analysis

#### Lỗi 1: Double Labeling (Đã fix trước đó)
- Complex filter đã có output, nhưng code cố thêm label `[v_main]` trùng lặp

#### Lỗi 2: Pre-Filter Not Wrapped (Lỗi mới phát hiện)
**Filter chain SAI:**
```
scale=iw*0.6:ih*1.4,split[bg][fg];[bg]scale=720:1280:...,boxblur=...[bg_blur];...
```

**Vấn đề**: 
- `split` cần input từ `[0:v]` hoặc một labeled stream
- Nhưng `scale=iw*0.6:ih*1.4` không có label output
- Dẫn đến `split` nhận input không xác định → **SYNTAX ERROR**

**Filter chain ĐÚNG:**
```
[0:v]scale=iw*0.6:ih*1.4[pre];[pre]split[bg][fg];[bg]scale=720:1280:...,boxblur=...[bg_blur];...
```

### 🛠️ Solution Implementation

#### File: `utils/video_processor.py`

**BEFORE (Broken):**
```python
# Add scale to filters list
if scale_w != 1.0 or scale_h != 1.0:
    filters.append(f"scale=iw*{scale_w}:ih*{scale_h}")

# Later: Add blur background
if enable_blur and blur_amount > 0:
    complex_part = (
        f"split[bg][fg];"  # ❌ No input label!
        f"[bg]scale=...,boxblur=...[bg_blur];"
        ...
    )
    filters.append(complex_part)  # ❌ Appends to list with scale filter
```

**AFTER (Fixed):**
```python
# Add scale to filters list
if scale_w != 1.0 or scale_h != 1.0:
    filters.append(f"scale=iw*{scale_w}:ih*{scale_h}")

# Later: Add blur background
if enable_blur and blur_amount > 0:
    # ✅ Build pre-filter chain from ALL previous filters
    pre_filters = ','.join(filters) if filters else None
    
    if pre_filters:
        # ✅ Wrap pre-filters with [0:v] input and [pre] output
        complex_part = (
            f"[0:v]{pre_filters}[pre];"
            f"[pre]split[bg][fg];"  # ✅ Now has valid input!
            f"[bg]scale=...,boxblur=...[bg_blur];"
            ...
        )
    else:
        # No pre-filters, split directly from [0:v]
        complex_part = (
            f"split[bg][fg];"
            ...
        )
    
    # ✅ REPLACE filters list (not append)
    filters = [complex_part]
```

### 📊 Test Results

#### Test Case 1: Scale + Blur BG + Sticker
**Input Settings:**
- Scale: W=0.6, H=1.4
- Brightness: 0.2
- Mirror: Yes
- Aspect Ratio: 9:16 (Fit mode)
- Blur: 5.67
- Sticker: Heart (20%, bottom-right)

**Generated Filter Chain:**
```
[0:v]scale=iw*0.6:ih*1.4,eq=brightness=0.2,hflip[pre];
[pre]split[bg][fg];
[bg]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=11.35:5.67[bg_blur];
[fg]scale=720:1280:force_original_aspect_ratio=decrease[fg_sized];
[bg_blur][fg_sized]overlay=(W-w)/2:(H-h)/2[v_main];
[1:v][v_main]scale2ref=w=iw*0.2:h=-1[stk][bg];
[bg][stk]overlay=W-w-20:H-h-20
```

**Result:** ✅ **VALID SYNTAX - 7 PARTS**

#### Test Case 2: No Pre-Filters + Blur BG + Sticker
**Input Settings:**
- Aspect Ratio: 9:16 (Fit mode)
- Blur: 10
- Sticker: Fire (15%, center)

**Generated Filter Chain:**
```
split[bg][fg];
[bg]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=20:10[bg_blur];
[fg]scale=720:1280:force_original_aspect_ratio=decrease[fg_sized];
[bg_blur][fg_sized]overlay=(W-w)/2:(H-h)/2[v_main];
[1:v][v_main]scale2ref=w=iw*0.15:h=-1[stk][bg];
[bg][stk]overlay=(W-w)/2:(H-h)/2
```

**Result:** ✅ **VALID SYNTAX - 6 PARTS**

### 🎯 Key Changes Summary

1. **Pre-Filter Detection**: Detect all filters before blur background
2. **Proper Wrapping**: Wrap pre-filters with `[0:v]...[pre]` labels
3. **List Replacement**: Replace filters list instead of appending
4. **Smart Input**: Use `[pre]` or `[0:v]` as split input based on pre-filters existence

### 📝 Code Changes

**File Modified:** `utils/video_processor.py`  
**Lines Changed:** 137-165  
**Complexity:** High (9/10)  
**Impact:** Critical - Fixes all scale + blur + sticker combinations

### ✅ Verification Steps

1. **Test 1**: Scale only → ✅ Works
2. **Test 2**: Blur BG only → ✅ Works
3. **Test 3**: Sticker only → ✅ Works
4. **Test 4**: Scale + Blur BG → ✅ Works
5. **Test 5**: Blur BG + Sticker → ✅ Works
6. **Test 6**: Scale + Sticker → ✅ Works
7. **Test 7**: Scale + Blur BG + Sticker → ✅ **NOW WORKS!**

### 🚀 How to Use

1. Open app
2. Select video
3. **Transform Tab:**
   - Adjust Scale W/H (e.g., 0.6 / 1.4)
   - Enable Brightness, Mirror, etc.
4. **Aspect Ratio:**
   - Choose 9:16 (TikTok/Shorts)
   - Mode: "Thêm viền (Fit)"
   - Enable Blur, set to ~10
5. **Sticker Tab:**
   - Select ❤️ Heart or any sticker
   - Position: Góc phải dưới
   - Scale: 0.2 (20%)
6. Click **"XUẤT VIDEO / BẮT ĐẦU"**

**Expected Result:** ✅ Video renders successfully with all effects applied!

### 📚 Technical Notes

#### FFmpeg Filter Graph Structure
```
[input] → [pre-filters] → [split] → [bg-path] → [overlay] → [sticker] → [output]
                            ↓
                         [fg-path] ↗
```

#### Label Flow
- `[0:v]` - Input video
- `[pre]` - After pre-filters (scale, brightness, etc.)
- `[bg]` / `[fg]` - Split streams
- `[bg_blur]` - Blurred background
- `[fg_sized]` - Scaled foreground
- `[v_main]` - After overlay
- `[stk]` / `[bg]` - Sticker and background for final overlay
- (unlabeled) - Final output

---

**Fixed by:** Nguyen Duy Duc  
**Date:** 2026-01-10  
**Version:** 1.0.2  
**Status:** ✅ **PRODUCTION READY**
