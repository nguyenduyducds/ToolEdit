# Hướng Dẫn Build Installer với Inno Setup

## Bước 1: Cài đặt Inno Setup

1. Tải Inno Setup từ: https://jrsoftware.org/isdl.php
2. Cài đặt Inno Setup (chọn "Full installation")
3. Khởi động lại terminal sau khi cài

## Bước 2: Build EXE với PyInstaller

Trước tiên, cần build executable:

```bash
python build_final.py
```

Hoặc nếu đã có file `dist\VideoEditorPro\VideoEditorPro.exe`, bỏ qua bước này.

## Bước 3: Build Installer

### Cách 1: Dùng GUI (Khuyến nghị cho lần đầu)

1. Mở Inno Setup Compiler
2. File → Open → Chọn `VideoEditorPro_Setup.iss`
3. Build → Compile (hoặc nhấn F9)
4. File installer sẽ được tạo trong thư mục `installer\`

### Cách 2: Dùng Command Line

```bash
# Nếu Inno Setup đã trong PATH
iscc VideoEditorPro_Setup.iss

# Hoặc dùng đường dẫn đầy đủ
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VideoEditorPro_Setup.iss
```

## Bước 4: Kiểm tra Output

Sau khi build thành công, file installer sẽ ở:
```
installer\VideoEditorPro_Setup_v2.0.2.exe
```

## Tính Năng Installer

✅ **Tự động tạo thư mục**:
   - `input\` - Thư mục video đầu vào
   - `output\` - Thư mục video đầu ra

✅ **Desktop Icon**: Tùy chọn tạo shortcut trên Desktop

✅ **File Association**: Liên kết với file `.vep` (Video Editor Pro project)

✅ **Uninstaller**: Tự động tạo uninstaller

✅ **Registry Keys**: Đăng ký app với Windows

## Troubleshooting

### Lỗi: "Cannot find file"
- Kiểm tra xem `dist\VideoEditorPro\VideoEditorPro.exe` có tồn tại không
- Chạy lại `python build_final.py`

### Lỗi: "License file not found"
- File `LICENSE.txt` đã được tạo tự động
- Nếu vẫn lỗi, comment dòng `LicenseFile=LICENSE.txt` trong `.iss`

### Lỗi: "Icon file not found"
- Dòng `SetupIconFile` đã được comment
- Installer sẽ dùng icon mặc định của Windows

## Tùy Chỉnh

Để thay đổi cấu hình installer, chỉnh sửa file `VideoEditorPro_Setup.iss`:

- **Đổi tên output**: Sửa `OutputBaseFilename`
- **Thêm icon**: Uncomment `SetupIconFile` và thêm file `.ico` vào `assets\`
- **Đổi thư mục cài đặt**: Sửa `DefaultDirName`
- **Thêm file**: Thêm dòng `Source` trong section `[Files]`

## Build Script Tự Động (PowerShell)

Tạo file `build_installer.ps1`:

```powershell
# Build EXE
Write-Host "Building EXE..." -ForegroundColor Cyan
python build_final.py

# Build Installer
Write-Host "Building Installer..." -ForegroundColor Cyan
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VideoEditorPro_Setup.iss

Write-Host "Done! Installer: installer\VideoEditorPro_Setup_v2.0.2.exe" -ForegroundColor Green
```

Chạy: `.\build_installer.ps1`
