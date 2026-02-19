"""Video Editor Pro - Main Entry Point"""

import sys
import tkinter as tk
import customtkinter as ctk
import os

# Fix DPI Scaling on Windows (CRITICAL for high-DPI displays)
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # System DPI aware
except:
    pass

# Configure CustomTkinter
ctk.set_appearance_mode("Dark")

# Set widget scaling (increase UI size)
ctk.set_widget_scaling(1.0)  # 100% - default size (back to original)
ctk.set_window_scaling(1.0)  # Keep window size normal

# Use custom theme with transparent label backgrounds
custom_theme_path = os.path.join(os.path.dirname(__file__), "assets", "themes", "custom_theme.json")
if os.path.exists(custom_theme_path):
    ctk.set_default_color_theme(custom_theme_path)
else:
    ctk.set_default_color_theme("green")  # Fallback

# Try to import tkinterdnd2 for drag & drop support
TKDND_AVAILABLE = False
try:
    from tkinterdnd2 import TkinterDnD
    TKDND_AVAILABLE = True
except ImportError:
    pass

# Define Root Class supporting CTk + DnD
if TKDND_AVAILABLE:
    class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
else:
    class CTkDnD(ctk.CTk):
        pass

# Import GUI
from UI.main_window import VideoEditorGUI

def show_copyright_splash():
    """Show copyright splash screen (Modern CTk Version)"""
    splash = ctk.CTk()
    splash.overrideredirect(True)
    
    # Dimensions
    w, h = 500, 300
    screen_w = splash.winfo_screenwidth()
    screen_h = splash.winfo_screenheight()
    x = (screen_w - w) // 2
    y = (screen_h - h) // 2
    splash.geometry(f"{w}x{h}+{x}+{y}")
    
    # Frame with border
    main_frame = ctk.CTkFrame(splash, corner_radius=10, border_width=2, border_color="#e94560")
    main_frame.pack(fill='both', expand=True, padx=2, pady=2)
    
    # Content
    ctk.CTkLabel(main_frame, text="🎬 Video Editor Pro", font=('Segoe UI', 24, 'bold'), text_color="#e94560").pack(pady=(30, 5))
    ctk.CTkLabel(main_frame, text="Version 2.0 - Reborn", font=('Segoe UI', 12), text_color="#a8a8a8").pack(pady=(0, 20))
    
    # Separator line
    ctk.CTkProgressBar(main_frame, height=2, progress_color="#e94560", width=400).pack(pady=10)
    
    ctk.CTkLabel(main_frame, text="© 2026 Bản quyền thuộc về", font=('Segoe UI', 12)).pack(pady=(20, 0))
    ctk.CTkLabel(main_frame, text="💖 Dev BÉ Đức Cute 💖", font=('Segoe UI', 20, 'bold'), text_color="#00d4ff").pack(pady=(5, 10))
    
    loading_lbl = ctk.CTkLabel(main_frame, text="Đang khởi động...", font=('Segoe UI', 10, 'italic'))
    loading_lbl.pack(pady=(5, 20))
    
    # Auto close
    splash.after(2500, splash.destroy)
    splash.mainloop()

def main():
    """Main entry point"""
    # Create required directories
    for directory in ['input', 'output', 'srt_files']:
        os.makedirs(directory, exist_ok=True)
    
    # Show splash
    show_copyright_splash()
    

    # Check dependencies (FFmpeg)
    # Using a dummy root for the dialog if needed, or pass the Splash
    # But Splash is blocking. Let's do it after Splash or INTEGRATE it.
    
    # Let's verify FFmpeg existence
    from utils.dependency_installer import DependencyInstaller
    
    installer = DependencyInstaller()
    if not installer.is_ffmpeg_installed():
        # Hide splash if it was still running (it runs its own mainloop in the current code, which blocks)
        # Actually show_copyright_splash() blocks until it closes (2.5s). 
        # So we check AFTER splash.
        
        # We need a root for the installer dialog
        # Use a temporary hidden root or just create one
        chk_root = ctk.CTk()
        chk_root.withdraw() # Hide main win
        
        # Ask user
        msg = "FFmpeg chưa được cài đặt (cần thiết để xử lý video).\nBạn có muốn tải và cài đặt tự động không?\n(Dung lượng ~100MB)"
        resp = tk.messagebox.askyesno("Thiếu thành phần", msg)
        
        if resp:
            # Show install GUI
            # We need to make chk_root visible or use it as parent
            chk_root.deiconify()
            chk_root.title("Video Editor Pro - Setup")
            chk_root.geometry("400x100")
            
            # Simple wrapper to wait for callback
            finished = [False]
            def on_done(success):
                finished[0] = True
                chk_root.quit()
                if not success:
                    tk.messagebox.showerror("Lỗi", "Cài đặt thất bại. Vui lòng thử lại hoặc cài thủ công.")
                    sys.exit(1)
            
            # Use the installer logic
            # We reused the installer class but modified to work with this ad-hoc root
            installer.root = chk_root
            installer.install_ffmpeg_gui(on_done)
            chk_root.mainloop() 
            chk_root.destroy()
            
        else:
            tk.messagebox.showwarning("Cảnh báo", "Ứng dụng có thể không hoạt động đúng nếu thiếu FFmpeg.")
    
    # Main App Window
    root = CTkDnD()
    
    # Set icon if exists (optional)
    # root.iconbitmap("icon.ico")
    
    app = VideoEditorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
