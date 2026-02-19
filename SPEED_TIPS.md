# ⚡ SPEED TIPS - ĐỂ RENDER NHANH NHẤT

## 🚀 **Settings Nhanh Nhất (Không Lỗi)**

### ✅ **Đã Tối Ưu Encoding**
- GPU: Preset `p3` (nhanh + ổn định)
- CPU: Preset `faster` (nhanh + ổn định)
- Bitrate: 2800k (thấp hơn = nhanh hơn)
- GOP: 60 (tối ưu cho tốc độ)

---

## 🎯 **Cách Render Nhanh Nhất**

### 1. **TẮT Blur Background** ⚡⚡⚡
**Quan trọng nhất!** Blur background tốn **50-70% thời gian render**!

**Cách:**
- Tab "Hình ảnh"
- Bỏ tick "Làm mờ (Blur)"
- **Tốc độ tăng**: 2-3x nhanh hơn!

### 2. **TẮT Subtitle** ⚡⚡
Subtitle processing tốn thời gian.

**Cách:**
- Tab "Cấu hình"
- Bỏ tick "Enable Subtitles"
- **Tốc độ tăng**: 20-30% nhanh hơn

### 3. **TẮT Color Filter** ⚡
Color filters (Cold, Warm, Vintage) tốn CPU.

**Cách:**
- Tab "Hình ảnh"
- Chọn "Gốc (None)" cho "Bộ lọc màu"
- **Tốc độ tăng**: 10-15% nhanh hơn

### 4. **Giảm Scale Transform** ⚡
Scale W/H khác 1.0 tốn thời gian.

**Cách:**
- Tab "Hình ảnh"
- Set Width = 1.0, Height = 1.0
- **Tốc độ tăng**: 5-10% nhanh hơn

### 5. **Dùng GPU** ⚡⚡⚡
GPU luôn nhanh hơn CPU 2-3x.

**Cách:**
- Đảm bảo GPU được bật (check log: "GPU=YES")
- Đóng game/app dùng GPU
- **Tốc độ tăng**: 2-3x nhanh hơn CPU

---

## 📊 **So Sánh Tốc Độ**

### Video 1 phút, 9:16, GPU

| Settings | Time | Speed |
|----------|------|-------|
| **Tất cả hiệu ứng** | ~5-7 phút | Baseline |
| **Tắt Blur** | ~2-3 phút | **2x nhanh hơn** |
| **Tắt Blur + Subtitle** | ~1.5-2 phút | **3x nhanh hơn** |
| **Chỉ resize** | ~1-1.5 phút | **4x nhanh hơn** |

---

## 🎯 **Settings Khuyến Nghị**

### **Nhanh Nhất (Chất lượng OK)**
```
✅ Aspect Ratio: 9:16
✅ Resize Mode: Thêm viền (Fit)
❌ Blur: OFF
❌ Subtitle: OFF
❌ Color Filter: None
❌ Scale W/H: 1.0 / 1.0
✅ Sticker: ON (không ảnh hưởng nhiều)
✅ Speed: 1.0
✅ Mirror: OFF
```

**Thời gian**: ~1-2 phút/video (GPU)

### **Cân Bằng (Nhanh + Đẹp)**
```
✅ Aspect Ratio: 9:16
✅ Resize Mode: Thêm viền (Fit)
❌ Blur: OFF (hoặc < 5)
✅ Subtitle: ON
✅ Color Filter: Cold/Warm
✅ Sticker: ON
```

**Thời gian**: ~2-3 phút/video (GPU)

### **Chất Lượng Cao (Chậm)**
```
✅ Tất cả hiệu ứng ON
✅ Blur: 10-15
✅ Subtitle: ON
✅ Color Filter: Vintage
```

**Thời gian**: ~5-7 phút/video (GPU)

---

## 💡 **Pro Tips**

### 1. **Batch Processing**
- Render nhiều video cùng lúc (3 threads)
- Tổng thời gian ít hơn render từng video

### 2. **Close Other Apps**
- Đóng Chrome, Discord, game
- Giải phóng RAM → Tăng threads
- Giải phóng GPU → Encoding nhanh hơn

### 3. **SSD vs HDD**
- Nếu có SSD, set input/output folder trên SSD
- SSD nhanh hơn HDD ~2x cho I/O

### 4. **Giảm Resolution Input**
- Video 4K → Render chậm
- Video 1080p → Render nhanh hơn
- Video 720p → Render nhanh nhất

---

## ⚠️ **Lưu Ý**

### **Blur Background = Chậm Nhất!**
Nếu bạn muốn nhanh, **TUYỆT ĐỐI TẮT BLUR**!

Blur background tốn:
- 50-70% thời gian render
- Nhiều CPU/GPU
- Nhiều RAM

**Giải pháp**:
- Dùng Resize Mode = "Lấp đầy (Fill)" thay vì Blur
- Hoặc chấp nhận viền đen (Fit mode, no blur)

---

## 🎬 **Kết Luận**

**Muốn nhanh nhất:**
1. ❌ Tắt Blur
2. ❌ Tắt Subtitle
3. ✅ Dùng GPU
4. ✅ Đóng app khác

**Kết quả**: Render ~1-2 phút/video thay vì 5-7 phút!

---

**Áp dụng ngay và thấy sự khác biệt!** ⚡🚀
