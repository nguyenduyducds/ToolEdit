
import os
import sys
import requests
import zipfile
import subprocess
import shutil
import threading
import customtkinter as ctk
from tkinter import messagebox

FFMPEG_URL = "https://github.com/GyanD/codexffmpeg/releases/download/2025-01-26-git-7c98033005/ffmpeg-2025-01-26-git-7c98033005-full_build.zip"
# Backup/Mirror URL if above fails is hard to predict, but we can stick to one for now or use a generic "latest" link carefully.
# Gyan.dev is standard for Windows.

class DependencyInstaller:
    def __init__(self, root_window=None):
        self.root = root_window
        self.install_dir = os.path.join(os.getcwd(), "bin")
        self.ffmpeg_exe = os.path.join(self.install_dir, "ffmpeg.exe")
        self.download_active = False

    def is_ffmpeg_installed(self):
        # Check local bin first
        if os.path.exists(self.ffmpeg_exe):
            return True
        # Check system path
        if shutil.which("ffmpeg"):
            return True
        return False

    def install_ffmpeg_gui(self, on_complete):
        """Show a GUI window for downloading FFmpeg"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Installing Dependencies")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        if self.root:
            x = self.root.winfo_x() + (self.root.winfo_width()//2) - 200
            y = self.root.winfo_y() + (self.root.winfo_height()//2) - 100
            dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text="Đang tải và cài đặt FFmpeg...", font=("Segoe UI", 14, "bold")).pack(pady=20)
        
        status_lbl = ctk.CTkLabel(dialog, text="Khởi tạo...", font=("Segoe UI", 12))
        status_lbl.pack(pady=5)
        
        progress = ctk.CTkProgressBar(dialog, width=300)
        progress.pack(pady=20)
        progress.set(0)

        def run_install():
            try:
                os.makedirs(self.install_dir, exist_ok=True)
                
                # 1. Download
                status_lbl.configure(text="Đang tải xuống (khoảng 100MB)...")
                
                # Using known stable link or generic
                # Note: This is an example URL. In production, ensure it's stable.
                url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" 
                
                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                
                zip_path = os.path.join(self.install_dir, "ffmpeg.zip")
                
                block_size = 1024 * 1024 # 1MB
                wrote = 0
                
                with open(zip_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        wrote += len(data)
                        f.write(data)
                        if total_size > 0:
                            perc = wrote / total_size
                            progress.set(perc)
                            dialog.update_idletasks()
                
                # 2. Extract
                status_lbl.configure(text="Đang giải nén...")
                progress.set(0.95) # Indeterminate
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Find the ffmpeg.exe inside the zip (it's usually in a subfolder)
                    # We extract specific file to bin
                    for file in zip_ref.namelist():
                        if file.endswith("ffmpeg.exe"):
                            source = zip_ref.open(file)
                            target = open(self.ffmpeg_exe, "wb")
                            with source, target:
                                shutil.copyfileobj(source, target)
                                
                        if file.endswith("ffprobe.exe"):
                             source = zip_ref.open(file)
                             target = open(os.path.join(self.install_dir, "ffprobe.exe"), "wb")
                             with source, target:
                                shutil.copyfileobj(source, target)
                                
                # Cleanup
                os.remove(zip_path)
                
                status_lbl.configure(text="Hoàn tất!")
                progress.set(1.0)
                dialog.after(1000, dialog.destroy)
                if on_complete:
                    on_complete(True)
                    
            except Exception as e:
                status_lbl.configure(text=f"Lỗi: {str(e)}")
                print(f"Install Error: {e}")
                dialog.after(3000, dialog.destroy)
                if on_complete:
                    on_complete(False)

        threading.Thread(target=run_install, daemon=True).start()
