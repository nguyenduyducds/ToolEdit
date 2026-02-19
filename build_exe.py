import PyInstaller.__main__
import os
import shutil

# Tên file exe đầu ra
APP_NAME = "VideoEditorPro"

# Đường dẫn đến file chính
MAIN_SCRIPT = "main.py"

# Các thư mục cần copy vào (PyInstaller --add-data format: 'src;dest')
add_data = [
    'assets;assets',
    'utils;utils',
    'UI;UI',
]

# Hidden imports (các thư viện mà PyInstaller có thể không tự tìm thấy)
hidden_imports = [
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'imageio',
    'imageio_ffmpeg',
    'moviepy',
    'ttkbootstrap',
    'tkinter',
    'sys',
    'os',
    're',
    'threading',
    'subprocess'
]

# Xây dựng command arguments
args = [
    MAIN_SCRIPT,
    f'--name={APP_NAME}',
    '--noconfirm',            # Ghi đè thư mục dist cũ
    '--windowed',             # Ẩn cửa sổ console (nếu muốn hiện để debug thì bỏ dòng này)
    '--onedir',               # Build ra 1 thư mục (khuyên dùng để dễ update custom file)
    '--clean',                # Dọn dẹp cache
    # '--onefile',            # Build ra 1 file exe duy nhất (khởi động chậm hơn và khó debug path)
]

# Thêm hidden imports
for imp in hidden_imports:
    args.append(f'--hidden-import={imp}')

# Thêm data files
for item in add_data:
    if ';' in item:
        src, dest = item.split(';')
        if os.path.exists(src):
            args.append(f'--add-data={item}')
        else:
            print(f"⚠️ Warning: Folder '{src}' not found, skipping...")

# Chạy PyInstaller
print("🚀 Đang build EXE... Vui lòng chờ...")
PyInstaller.__main__.run(args)

print("\n✅ BUILD HOÀN TẤT!")
print(f"👉 File EXE nằm trong thư mục: dist/{APP_NAME}/")
print("⚠️ Đừng quên copy folder 'ffmpeg' hoặc file 'ffmpeg.exe' vào thư mục dist nếu chưa có!")
