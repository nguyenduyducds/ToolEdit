# ✅ TEXT OUTRO IMPLEMENTATION - COMPLETE GUIDE

## 🎯 ĐÃ HOÀN THÀNH

### 1️⃣ Tạo Text Outro Generator
✅ File: `utils/text_outro_generator.py`
- Function `create_text_outro_video()` với đầy đủ customization
- Support: font size, colors, position, background, animation

### 2️⃣ Thêm UI Settings
✅ File: `UI/main_window.py`
- Variables (dòng 665-673): 8 settings mới
- UI (dòng 2029-2050): 5 comboboxes custom

### 3️⃣ CẦN LÀM TIẾP (INTEGRATION)

**File:** `UI/main_window.py` - Function `start_processing()`

Thêm text outro settings vào dict settings (sau dòng 2722):

```python
# Text Outro (NEW)
'enable_outro_text': self.enable_outro_text.get(),
'outro_text_duration': self.outro_text_duration.get(),
'outro_text_content': self.outro_text_content.get(),
'outro_text_font_size': self.outro_text_font_size.get(),
'outro_text_font_color': self.outro_text_font_color.get(),
'outro_text_bg_color': self.outro_text_bg_color.get(),
'outro_text_position': self.outro_text_position.get(),
'outro_text_animation': self.outro_text_animation.get(),
```

---

**File:** `UI/main_window.py` - Function `process_queue()`

Sau khi xử lý video (dòng ~3020), thêm logic tạo và concat text outro:

```python
# After video processing success
if settings.get('enable_outro_text') and settings.get('outro_text_content'):
    log("   📝 Creating text outro...")
    
    from utils.text_outro_generator import create_text_outro_video
    import tempfile
    
    # Create text outro video
    text_outro_path = os.path.join(tempfile.gettempdir(), f"text_outro_{filename}.mp4")
    
    result = create_text_outro_video(
        text=settings['outro_text_content'],
        duration=settings.get('outro_text_duration', 5),
        output_path=text_outro_path,
        width=1080,  # Match aspect ratio
        height=1920,
        font_size=settings.get('outro_text_font_size', 60),
        font_color=settings.get('outro_text_font_color', 'white'),
        bg_color=settings.get('outro_text_bg_color', 'black'),
        position=settings.get('outro_text_position', 'center'),
        animation=settings.get('outro_text_animation', 'fade'),
        log_callback=log
    )
    
    if result:
        log("   🔗 Concatenating text outro...")
        
        # Concat main video + text outro
        concat_list = os.path.join(tempfile.gettempdir(), f"concat_list_{filename}.txt")
        with open(concat_list, 'w') as f:
            f.write(f"file '{output_path}'\n")
            f.write(f"file '{text_outro_path}'\n")
        
        final_output = output_path.replace('.mp4', '_with_outro.mp4')
        
        concat_cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list,
            '-c', 'copy',
            '-y',
            final_output
        ]
        
        subprocess.run(concat_cmd, capture_output=True)
        
        # Replace original with concatenated
        if os.path.exists(final_output):
            os.replace(final_output, output_path)
            log("   ✅ Text outro added!")
        
        # Cleanup
        try:
            os.remove(text_outro_path)
            os.remove(concat_list)
        except:
            pass
```

---

## 🧪 TESTING

### Test 1: Tạo Text Outro Riêng
```bash
cd utils
python text_outro_generator.py
# Should create test_outro.mp4
```

### Test 2: Full Integration
1. Chạy app: `python main.py`
2. Thêm 1 video
3. Bật "Hiển thị Text cuối video"
4. Nhập text: "Thanks for watching!"
5. Chọn: Font 80, White, Black bg, Center, Fade
6. Click "XUẤT VIDEO"
7. Check output video có text outro không

---

## 📝 CUSTOMIZATION OPTIONS

| Option | Values | Mô tả |
|--------|--------|-------|
| **Font Size** | 40-100 | Kích thước chữ |
| **Text Color** | white, black, red, blue... | Màu chữ |
| **Background** | black, white, gradient | Nền |
| **Position** | center, top, bottom | Vị trí text |
| **Animation** | none, fade, slide_up, slide_down | Hiệu ứng |

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Font not found"
- Windows: Font path `/Windows/Fonts/arial.ttf`
- Nếu không có, đổi thành font khác hoặc bỏ `fontfile`

### Lỗi: "Concat failed"
- Check video codec compatibility
- Ensure both videos have same resolution/fps

### Text không hiện
- Check text content không rỗng
- Check font color != background color

---

**🚀 Sau khi thêm integration code, tính năng sẽ hoạt động 100%!**
