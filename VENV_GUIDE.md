# 🔧 Hướng dẫn sử dụng Virtual Environment

## 📦 Virtual Environment đã được tạo!

Thư mục `venv/` chứa môi trường Python riêng biệt cho project này.

---

## 🚀 Cách sử dụng

### 1. Kích hoạt Virtual Environment

#### Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

#### Windows (CMD):
```cmd
venv\Scripts\activate.bat
```

#### Linux/Mac:
```bash
source venv/bin/activate
```

**Sau khi kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng lệnh:**
```
(venv) C:\Users\Admin\Desktop\ToolEdit>
```

---

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

**Hoặc cài từng package:**
```bash
pip install tkinterdnd2
pip install moviepy
pip install openai-whisper
pip install SpeechRecognition
pip install imageio-ffmpeg
pip install pillow
pip install numpy
pip install scipy
pip install psutil
pip install requests
```

---

### 3. Chạy ứng dụng

```bash
python main.py
```

---

### 4. Tắt Virtual Environment

```bash
deactivate
```

---

## 📝 Lợi ích của Virtual Environment

✅ **Tách biệt dependencies** - Không ảnh hưởng đến Python system
✅ **Dễ quản lý** - Mỗi project có dependencies riêng
✅ **Dễ deploy** - Export requirements.txt dễ dàng
✅ **Tránh conflict** - Các version khác nhau không xung đột

---

## 🔍 Kiểm tra

### Xem packages đã cài:
```bash
pip list
```

### Xem thông tin Python:
```bash
python --version
which python  # Linux/Mac
where python  # Windows
```

### Export dependencies:
```bash
pip freeze > requirements.txt
```

---

## ⚠️ Lưu ý

### Nếu gặp lỗi PowerShell:
```
.\venv\Scripts\Activate.ps1 : File cannot be loaded because running scripts is disabled
```

**Giải pháp:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Sau đó chạy lại:
```powershell
.\venv\Scripts\Activate.ps1
```

---

## 📂 Cấu trúc thư mục venv

```
venv/
├── Scripts/          # Executables (Windows)
│   ├── activate.bat
│   ├── Activate.ps1
│   ├── python.exe
│   └── pip.exe
│
├── Lib/              # Python libraries
│   └── site-packages/
│
└── pyvenv.cfg        # Config file
```

---

## 🎯 Workflow khuyến nghị

### Lần đầu setup:
```bash
# 1. Tạo venv (đã làm rồi)
python -m venv venv

# 2. Kích hoạt
.\venv\Scripts\Activate.ps1

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Chạy app
python main.py
```

### Mỗi lần làm việc:
```bash
# 1. Kích hoạt venv
.\venv\Scripts\Activate.ps1

# 2. Chạy app
python main.py

# 3. Tắt venv khi xong
deactivate
```

---

## 🔄 Update dependencies

### Thêm package mới:
```bash
# Kích hoạt venv
.\venv\Scripts\Activate.ps1

# Cài package
pip install <package-name>

# Update requirements.txt
pip freeze > requirements.txt
```

### Xóa package:
```bash
pip uninstall <package-name>
pip freeze > requirements.txt
```

---

## 🗑️ Xóa và tạo lại venv

### Xóa venv:
```bash
# Tắt venv trước
deactivate

# Xóa thư mục
rmdir /s venv  # Windows
rm -rf venv    # Linux/Mac
```

### Tạo lại:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## ✅ Checklist

- [x] Virtual environment đã tạo (`venv/`)
- [ ] Kích hoạt venv
- [ ] Cài đặt dependencies (`pip install -r requirements.txt`)
- [ ] Test chạy app (`python main.py`)

---

**🎉 Virtual Environment đã sẵn sàng!**

**Bước tiếp theo:**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
