# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('assets', 'assets'), ('UI', 'UI'), ('utils', 'utils'), ('core', 'core'), ('C:\\Users\\Admin\\.cache\\whisper', 'whisper_models'), ('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\whisper\\assets', 'whisper/assets'), ('srt_files', 'srt_files'), ('bin', 'bin')]
binaries = [('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\torch\\lib\\c10.dll', 'torch/lib'), ('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\torch\\lib\\libiomp5md.dll', 'torch/lib'), ('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\torch\\lib\\libiompstubs5md.dll', 'torch/lib'), ('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\torch\\lib\\shm.dll', 'torch/lib'), ('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\torch\\lib\\torch.dll', 'torch/lib'), ('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\torch\\lib\\torch_cpu.dll', 'torch/lib'), ('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\torch\\lib\\torch_global_deps.dll', 'torch/lib'), ('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\torch\\lib\\torch_python.dll', 'torch/lib'), ('C:\\Users\\Admin\\Desktop\\ToolEdit\\ToolEdit\\venv\\lib\\site-packages\\torch\\lib\\uv.dll', 'torch/lib')]
hiddenimports = ['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL.ImageDraw', 'PIL.ImageFont', 'imageio', 'imageio_ffmpeg', 'cv2', 'ttkbootstrap', 'whisper', 'torch', 'torch.nn', 'torch.nn.functional', 'torchaudio', 'numpy', 'scipy', 'scipy.signal', 'scipy.ndimage', 'requests', 'urllib3', 'certifi', 'charset_normalizer', 'pystray', 'customtkinter', 'faster_whisper', 'ctranslate2', 'subprocess', 'threading', 'multiprocessing', 'queue', 'json', 're', 'sys', 'os', 'pathlib', 'shutil', 'time', 'datetime']
tmp_ret = collect_all('tkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('ttkbootstrap')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoEditorPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version.txt',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='VideoEditorPro',
)
