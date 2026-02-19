"""Main window GUI for Video Editor Pro - CapCut Style"""

import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from tkinter.scrolledtext import ScrolledText
import webbrowser
import tempfile
from UI.modules.config_manager import ConfigManager, APP_VERSION, DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR
from UI.modules.custom_widgets import DraggableValueLabel

# --- CONFIGURATION ---
import cv2
from PIL import Image, ImageTk

# Import utils
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False
    TkinterDnD = None

# Imports from our modules
from config.settings import *
from core.update_checker import check_for_updates
from utils.helpers import detect_optimal_threads, get_video_files, GPU_ENCODE_SEMAPHORE
from utils.video_processor import process_video_with_ffmpeg, get_video_info
from utils.subtitle_generator import generate_subtitles_with_whisper, generate_subtitles_with_google
from utils.background_helper import enable_background_processing, notify_video_complete, notify_all_complete

# NEW: Preview player modules
from UI.preview_player import VideoPreviewPlayer
from utils.giphy_api import GiphyAPI

# --- THEME COLORS (Tuple: Light, Dark) ---
# Supports CustomTkinter appearance mode switching
COLOR_BG_MAIN = ("#E0E4E8", "#121212")
COLOR_BG_PANEL = ("#EDF1F5", "#1E1E1E")
COLOR_BG_HEADER = ("#D4D8DC", "#181818")
COLOR_BG_SECONDARY = ("#C8CCD0", "#2A2A2A")
COLOR_ACCENT = ("#0088CC", "#54D6E3")
COLOR_ACCENT_HOVER = ("#0099DD", "#7BE2ED")
COLOR_TEXT_PRIMARY = ("#2C3E50", "#FFFFFF")
COLOR_TEXT_SECONDARY = ("#555555", "#A1A1A1")
COLOR_BORDER = ("#BDC3C7", "#333333")
COLOR_BUTTON_BG = ("#D8DCE0", "#333333")
COLOR_SUCCESS = ("#27AE60", "#00CA74")
COLOR_WARNING = ("#F39C12", "#FFC107")
COLOR_ERROR = ("#E74C3C", "#FF4C4C")
COLOR_TRANSPARENT = ("transparent", "transparent")  # For labels that need transparent bg in both modes

# Theme Definitions
THEMES = {
    "dark": {
        "bg_main": "#121212",
        "bg_panel": "#1E1E1E",
        "bg_header": "#181818",
        "bg_secondary": "#2A2A2A",
        "accent": "#54D6E3",
        "accent_hover": "#7BE2ED",
        "text_primary": "#FFFFFF",
        "text_secondary": "#A1A1A1",
        "border": "#333333",
        "button_bg": "#333333",
        "success": "#00CA74",
        "warning": "#FFC107",
        "error": "#FF4C4C",
        "console_bg": "#111111",
        "console_fg": "#00FF88",
        "preview_bg": "#000000",
        "drop_zone_bg": "#2A2A2A"
    },
    "light": {
        "bg_main": "#E0E4E8",        # Xám xanh nhẹ (thay vì #F5F5F5)
        "bg_panel": "#EDF1F5",       # Xám xanh sáng (thay vì #FFFFFF)
        "bg_header": "#D4D8DC",      # Xám xanh đậm hơn (thay vì #E8E8E8)
        "bg_secondary": "#C8CCD0",   # Xám trung bình (thay vì #D0D0D0)
        "accent": "#0088CC",         # Xanh dương đậm hơn (thay vì #0099CC)
        "accent_hover": "#0099DD",   # Xanh dương sáng
        "text_primary": "#2C3E50",   # Xám đen mềm (thay vì #1A1A1A)
        "text_secondary": "#7F8C8D", # Xám trung bình (thay vì #666666)
        "border": "#BDC3C7",         # Xám nhạt (thay vì #CCCCCC)
        "button_bg": "#D8DCE0",      # Xám xanh nhạt (thay vì #E0E0E0)
        "success": "#27AE60",        # Xanh lá đậm hơn (thay vì #00AA55)
        "warning": "#F39C12",        # Cam đậm hơn (thay vì #FF9900)
        "error": "#E74C3C",          # Đỏ đậm hơn (thay vì #DD3333)
        "console_bg": "#ECF0F1",     # Xám xanh rất nhạt (thay vì #F8F8F8)
        "console_fg": "#16A085",     # Xanh lá biển (thay vì #008855)
        "preview_bg": "#D5D9DD",     # Xám xanh trung bình (thay vì #E0E0E0)
        "drop_zone_bg": "#DDE1E5"    # Xám xanh nhạt (thay vì #E8E8E8)
    }
}


# CRITICAL: Helper function to get current color from tuple
def get_color(color_tuple):
    """Extract current theme color from tuple (Light, Dark)"""
    if not isinstance(color_tuple, tuple):
        return color_tuple
    mode = ctk.get_appearance_mode().lower()
    return color_tuple[0] if mode == "light" else color_tuple[1]



class ModernButton(tk.Button):
    """Custom Button styling to look modern"""
    def __init__(self, master, text, command=None, bg=get_color(COLOR_ACCENT), fg="#000000", **kwargs):
        super().__init__(master, text=text, command=command, bg=bg, fg=fg, 
                         activebackground=get_color(COLOR_ACCENT_HOVER), activeforeground=fg,
                         relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"),
                         pady=8, padx=15, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.default_bg = bg

    def on_enter(self, e):
        self.config(bg=get_color(COLOR_ACCENT_HOVER) if self.default_bg == get_color(COLOR_ACCENT) else "#444444")

    def on_leave(self, e):
        self.config(bg=self.default_bg)


class VideoEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Video Editor Pro v{APP_VERSION} - CapCut Style")
        
        # Auto-maximize window to fit screen
        self.root.state('zoomed')  # Windows maximize
        
        # Set minimum size (reduced for smaller screens)
        self.root.minsize(1000, 700)
        self.root.configure(bg=COLOR_BG_MAIN)
        
        # Theme Management (NEW)
        self.current_theme = "dark"  # Default theme
        
        # Configure Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # --- Variables ---
        # --- Variables ---
        self.input_dir = tk.StringVar(value=DEFAULT_INPUT_DIR)
        
        # Processing State
        self.is_processing = False
        self.processed_files = set()
        self.stop_requested = False
        self.files_to_process = []
        
        # Configuration Manager
        self.config_manager = ConfigManager(self)
        
        # Settings Variables
        self.config_manager.init_settings_vars()
        
        # Preview State
        self.current_video_cap = None
        self.preview_thread = None
        self.stop_preview = False
        self.preview_id = 0 # Counter to manage preview threads
        
        # Sticker Interaction State (Runtime)
        self.sticker_dragging = False
        self.selected_sticker_idx = -1
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        # UI Layout
        self.setup_layout()
        
        # Initial Load
        os.makedirs(DEFAULT_INPUT_DIR, exist_ok=True)
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
        self.load_file_list()
        
        # Initialize Preview Player (NEW)
        self.preview_player = VideoPreviewPlayer(self)
        
        # System Tray Support
        self.tray_icon = None
        self.is_minimized_to_tray = False
        self.setup_system_tray()
        
        # Auto-load saved config
        self.config_manager.auto_load_config()
        
        # Clean up old temporary SRT files from previous sessions
        self.cleanup_old_srt_files()
        
        # Handle window close event (X button)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Background Checks
        threading.Thread(target=self.check_updates_bg, daemon=True).start()
    
    def setup_system_tray(self):
        """Setup system tray icon for background processing"""
        try:
            import pystray
            from PIL import Image, ImageDraw
            
            # Create a simple icon (you can replace with actual icon file)
            def create_icon_image():
                # Create a 64x64 icon with app initial
                img = Image.new('RGB', (64, 64), color=(84, 214, 227))  # get_color(COLOR_ACCENT)
                draw = ImageDraw.Draw(img)
                # Draw "V" for Video Editor
                draw.text((18, 18), "VE", fill=(0, 0, 0), font=None)
                return img
            
            # Create menu
            def on_show(icon, item):
                self.restore_from_tray()
            
            def on_exit(icon, item):
                self.quit_app()
            
            menu = pystray.Menu(
                pystray.MenuItem("Show Window", on_show, default=True),
                pystray.MenuItem("Exit", on_exit)
            )
            
            # Create tray icon (but don't run yet)
            self.tray_icon = pystray.Icon(
                "VideoEditorPro",
                create_icon_image(),
                "Video Editor Pro",
                menu
            )
            
        except ImportError:
            print("⚠️ pystray not installed. System tray disabled.")
            self.tray_icon = None
    
    def minimize_to_tray(self):
        """Minimize window to system tray"""
        if not self.tray_icon:
            self.log("   ⚠️ System tray not available, continuing in normal mode...")
            return
        
        try:
            # Hide window
            self.root.withdraw()
            self.is_minimized_to_tray = True
            
            # Start tray icon in background thread
            if not self.tray_icon.visible:
                def run_tray():
                    try:
                        self.tray_icon.run()
                    except Exception as e:
                        print(f"Tray icon thread error: {e}")
                        # Restore window if tray fails
                        self.root.after(100, self.restore_from_tray)
                
                threading.Thread(target=run_tray, daemon=True).start()
            
        except Exception as e:
            self.log(f"   ⚠️ Failed to minimize to tray: {e}")
            self.log("   Continuing in normal mode...")
            # Restore window if minimize failed
            try:
                self.root.deiconify()
                self.is_minimized_to_tray = False
            except:
                pass
    
    def restore_from_tray(self):
        """Restore window from system tray"""
        if not self.is_minimized_to_tray:
            return
        
        try:
            # Show window
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.is_minimized_to_tray = False
            
        except Exception as e:
            print(f"Failed to restore from tray: {e}")
    
    def show_notification(self, title, message):
        """Show system notification"""
        if self.tray_icon and self.is_minimized_to_tray:
            try:
                self.tray_icon.notify(message, title)
            except:
                pass
    
    def quit_app(self):
        """Quit application properly"""
        try:
            # Stop Preview
            self.stop_preview = True
            self.is_paused = False # Break pause loop
            
            # Stop Processing
            if self.is_processing:
                self.is_processing = False
                # Try to kill ffmpeg processes if possible (Best effort)
                try:
                    import subprocess
                    subprocess.run(["taskkill", "/F", "/IM", "ffmpeg.exe"], 
                                  capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                except: pass

            if self.tray_icon:
                self.tray_icon.stop()
        except:
            pass
            
        try:
            self.root.quit()
            self.root.destroy()
        except:
            sys.exit(0)

    
    def show_about_dialog(self):
        """Show About dialog with copyright information"""
        # Fix TclError: Extract colors for Tkinter
        mode = ctk.get_appearance_mode().lower()
        idx = 1 if mode == "dark" else 0
        def c(color): return color[idx] if isinstance(color, tuple) else color
        
        bg_panel = c('#0f3460') # Preserve original about color or use theme? Let's generic theme it.
        # Original used hardcoded #0f3460. Let's stick to theme for consistency? 
        # User wants "Light full giao diện".
        # Let's use theme constants.
        bg = c(get_color(COLOR_BG_PANEL))
        fg = c(get_color(COLOR_TEXT_PRIMARY))
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About Video Editor Pro")
        about_window.geometry("450x350")
        about_window.resizable(False, False)
        about_window.configure(bg=bg)
        
        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Main frame
        main_frame = tk.Frame(about_window, bg=bg, bd=3, relief='raised')
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # App Icon/Title
        title_label = tk.Label(
            main_frame,
            text="🎬 Video Editor Pro",
            font=('Segoe UI', 20, 'bold'),
            fg=c(get_color(COLOR_ACCENT)),
            bg=bg
        )
        title_label.pack(pady=(20, 5))
        
        # Version
        version_label = tk.Label(
            main_frame,
            text=f"Version {APP_VERSION}",
            font=('Segoe UI', 10),
            fg=fg,
            bg=bg
        )
        version_label.pack(pady=(0, 10))
        
        # Separator
        separator = tk.Frame(main_frame, height=2, bg=c(get_color(COLOR_ACCENT)))
        separator.pack(fill='x', padx=40, pady=15)
        
        # Copyright
        copyright_label = tk.Label(
            main_frame,
            text="© 2026 Bản quyền thuộc về",
            font=('Segoe UI', 11),
            fg=fg,
            bg=bg
        )
        copyright_label.pack(pady=(10, 5))
        
        # Developer name
        dev_label = tk.Label(
            main_frame,
            text="💖 Dev BÉ Đức Cute 💖",
            font=('Segoe UI', 18, 'bold'),
            fg='#00d4ff', # Keep signature color
            bg=bg
        )
        dev_label.pack(pady=(5, 15))
        
        # Description
        desc_label = tk.Label(
            main_frame,
            text="Professional Video Editing Tool\nPowered by FFmpeg & Whisper AI",
            font=('Segoe UI', 9),
            fg=c(get_color(COLOR_TEXT_SECONDARY)),
            bg=bg,
            justify='center'
        )
        desc_label.pack(pady=(10, 20))
        
        # Close button
        close_btn = tk.Button(
            main_frame,
            text="OK",
            font=('Segoe UI', 10, 'bold'),
            bg=c(get_color(COLOR_ERROR)),
            fg='#ffffff',
            activebackground='#ff5577',
            activeforeground='#ffffff',
            relief='flat',
            bd=0,
            padx=30,
            pady=8,
            cursor='hand2',
            command=about_window.destroy
        )
        close_btn.pack(pady=(0, 20))
        
        # Center on parent
        about_window.update_idletasks()
        try:
            x = self.root.winfo_x() + (self.root.winfo_width() - about_window.winfo_width()) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - about_window.winfo_height()) // 2
            about_window.geometry(f"+{x}+{y}")
        except: pass

    
    def on_closing(self):
        """Handle window close event (X button)"""
        # Check if processing
        if self.is_processing:
            from tkinter import messagebox
            result = messagebox.askyesno(
                "Confirm Exit",
                "Video processing is in progress. Are you sure you want to exit?\n\n"
                "This will stop all processing and close the application."
            )
            if not result:
                return  # Don't close
        
        # Auto-save config before exit
        self.config_manager.auto_save_config()
        
        # Stop tray icon and exit
        self.quit_app()

    def cleanup_old_srt_files(self):
        """Clean up old temporary SRT files from previous sessions"""
        try:
            srt_dir = "srt_files"
            if os.path.exists(srt_dir):
                srt_files = [f for f in os.listdir(srt_dir) if f.startswith("temp_subs_") and f.endswith(".srt")]
                if srt_files:
                    for srt_file in srt_files:
                        try:
                            os.remove(os.path.join(srt_dir, srt_file))
                        except:
                            pass
                    print(f"🗑️ Cleaned up {len(srt_files)} old subtitle file(s)")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")


    def configure_styles(self):
        """Configure TTK styles for dark/light theme"""
        # Determine current mode color index (0=Light, 1=Dark)
        mode = ctk.get_appearance_mode().lower()
        idx = 1 if mode == "dark" else 0
        
        def c(color): return color[idx] if isinstance(color, tuple) else color

        # Refresh styles
        bg_panel = c(get_color(COLOR_BG_PANEL))
        bg_main = c(COLOR_BG_MAIN)
        bg_header = c(get_color(COLOR_BG_HEADER))
        txt_primary = c(get_color(COLOR_TEXT_PRIMARY))
        txt_secondary = c(get_color(COLOR_TEXT_SECONDARY))
        accent = c(get_color(COLOR_ACCENT))
        border = c(get_color(COLOR_BORDER))
        
        # Global styling
        self.style.configure(".", background=bg_panel, foreground=txt_primary, font=("Segoe UI", 10))
        
        # Notebook (Tabs)
        self.style.configure("TNotebook", background=bg_main, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=bg_header, foreground=txt_secondary, 
                             padding=[20, 10], font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab", 
                       background=[("selected", bg_panel)], 
                       foreground=[("selected", accent)])
        
        # Treeview (List)
        self.style.configure("Treeview", 
                             background=bg_main, 
                             foreground=txt_primary,
                             fieldbackground=bg_main,
                             borderwidth=0,
                             rowheight=30,
                             font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", 
                             background=bg_header, 
                             foreground=txt_secondary,
                             font=("Segoe UI", 6, "bold"),  # Reduced from 9 to 8
                             relief="flat")
        
        sel_bg = "#333333" if idx == 1 else "#BDC3C7"
        self.style.map("Treeview", background=[("selected", sel_bg)], foreground=[("selected", txt_primary)])
        
        # Labelframes
        self.style.configure("TLabelframe", background=bg_panel, bordercolor=border)
        self.style.configure("TLabelframe.Label", background=bg_panel, foreground=accent, font=("Segoe UI", 10, "bold"))
        
        # PanedWindow
        self.style.configure("Sash", background=border, sashthickness=2)
        
        # Update Context Menu if it exists (tk widgets don't auto-update)
        if hasattr(self, 'context_menu'):
            try:
                bg_menu = c(get_color(COLOR_BG_SECONDARY))
                fg_menu = c(get_color(COLOR_TEXT_PRIMARY))
                acc = c(get_color(COLOR_ACCENT))
                self.context_menu.config(bg=bg_menu, fg=fg_menu, activebackground=acc, activeforeground="black")
            except: pass

    def update_all_widget_colors(self):
        """Update ALL widget colors when theme changes (Critical for Light Mode)"""
        mode = ctk.get_appearance_mode().lower()
        is_dark = mode == "dark"
        
        # Get current theme colors
        theme = THEMES["dark"] if is_dark else THEMES["light"]
        
        # Helper to update CTk widgets recursively
        def update_widget(widget):
            try:
                widget_type = type(widget).__name__
                
                # Update CTkLabel
                if widget_type == "CTkLabel":
                    # Check if it's a title/header (larger font)
                    try:
                        font = widget.cget("font")
                        if font and ("bold" in str(font).lower() or int(str(font).split()[1]) >= 14):
                            # Title/Header label
                            widget.configure(text_color=theme["accent"])
                        else:
                            # Normal label
                            widget.configure(text_color=theme["text_primary"])
                    except:
                        widget.configure(text_color=theme["text_primary"])
                
                # Update CTkCheckBox
                elif widget_type == "CTkCheckBox":
                    widget.configure(
                        text_color=theme["text_primary"],
                        fg_color=theme["accent"],
                        hover_color=theme["accent_hover"],
                        border_color=theme["border"]
                    )
                
                # Update CTkSlider
                elif widget_type == "CTkSlider":
                    widget.configure(
                        button_color=theme["accent"],
                        button_hover_color=theme["accent_hover"],
                        progress_color=theme["accent"],
                        fg_color=theme["bg_secondary"]
                    )
                
                # Update CTkEntry
                elif widget_type == "CTkEntry":
                    widget.configure(
                        text_color=theme["text_primary"],
                        fg_color=theme["bg_secondary"],
                        border_color=theme["border"]
                    )
                
                # Update CTkComboBox
                elif widget_type == "CTkComboBox":
                    widget.configure(
                        text_color=theme["text_primary"],
                        fg_color=theme["bg_secondary"],
                        border_color=theme["border"],
                        button_color=theme["accent"],
                        button_hover_color=theme["accent_hover"]
                    )
                
                # Update CTkFrame (only if it has explicit fg_color)
                elif widget_type == "CTkFrame":
                    try:
                        current_fg = widget.cget("fg_color")
                        # Only update if not transparent
                        if current_fg and current_fg != "transparent":
                            # Determine if it's a panel or secondary frame
                            if hasattr(widget, '_is_panel'):
                                widget.configure(fg_color=theme["bg_panel"])
                            else:
                                widget.configure(fg_color=theme["bg_secondary"])
                    except:
                        pass
                
                # Recursively update children
                try:
                    for child in widget.winfo_children():
                        update_widget(child)
                except:
                    pass
                    
            except Exception as e:
                pass  # Silently skip widgets that can't be updated
        
        # Start recursive update from root
        try:
            update_widget(self.root)
        except:
            pass
        
        # Force update display
        self.root.update_idletasks()

    def init_settings_vars(self):
        """Initialize all setting variables"""
        # Threads
        self.num_threads = tk.IntVar(value=detect_optimal_threads())
        self.preview_id = 0

        
        # Video
        self.start_time = tk.IntVar(value=DEFAULT_START_TIME)
        self.duration = tk.IntVar(value=0) # 0 = Full VideoByDefault
        self.blur_amount = tk.DoubleVar(value=DEFAULT_BLUR_AMOUNT)
        self.brightness = tk.DoubleVar(value=DEFAULT_BRIGHTNESS)
        self.zoom_factor = tk.DoubleVar(value=DEFAULT_ZOOM_FACTOR) # Legacy or for Pan/Zoom
        self.speed_factor = tk.DoubleVar(value=DEFAULT_SPEED_FACTOR)
        self.mirror_enabled = tk.BooleanVar(value=DEFAULT_MIRROR_ENABLED)
        
        # Aspect Ratio
        self.aspect_ratio = tk.StringVar(value="Giữ nguyên (Original)")
        self.resize_mode = tk.StringVar(value="Thêm viền (Fit)")
        
        # Transform Vars (New)
        self.uniform_scale = tk.BooleanVar(value=False)
        self.scale_w = tk.DoubleVar(value=1.0)
        self.scale_h = tk.DoubleVar(value=1.0)
        
        # Effect Toggles
        self.enable_zoom = tk.BooleanVar(value=False) # Default OFF
        self.enable_speed = tk.BooleanVar(value=False) # Default OFF
        self.enable_blur = tk.BooleanVar(value=False) # Default OFF
        self.enable_brightness = tk.BooleanVar(value=False) # Default OFF
        
        self.simple_mode = tk.BooleanVar(value=0)
        self.use_gpu = tk.BooleanVar(value=True) # Default ON for performance
        
        # Audio
        self.volume_boost = tk.DoubleVar(value=1.0)
        self.bass_boost = tk.DoubleVar(value=0)
        self.treble_boost = tk.DoubleVar(value=0)
        
        # Subtitle
        self.enable_subtitles = tk.BooleanVar(value=0) # Default OFF (User request)
        self.subtitle_language = tk.StringVar(value="auto (Tự động)")  # Default Auto-detect
        self.force_google_subs = tk.BooleanVar(value=0)
        
        # Subtitle Black Bar (NEW)
        self.enable_subtitle_bar = tk.BooleanVar(value=False)
        self.subtitle_bar_height = tk.IntVar(value=80)  # Height in pixels
        
        # System Tray (Background Processing)
        self.enable_minimize_to_tray = tk.BooleanVar(value=False)  # Default OFF to prevent crashes
        
        # Intro/Outro
        
        # Text Outro (NEW - Customizable)
        self.enable_outro_text = tk.BooleanVar(value=0)
        self.outro_text_content = tk.StringVar(value="Thanks for watching!")
        self.outro_text_duration = tk.IntVar(value=5)
        self.outro_text_font_size = tk.IntVar(value=60)
        self.outro_text_font_color = tk.StringVar(value="white")
        self.outro_text_bg_color = tk.StringVar(value="black")
        self.outro_text_position = tk.StringVar(value="center")
        self.outro_text_animation = tk.StringVar(value="fade")
        self.outro_text_box = tk.BooleanVar(value=False) # New boolean for text box background
        self.outro_text_box_padding = tk.IntVar(value=15) # Padding for text box (NEW)
        self.outro_text_style = tk.StringVar(value="Đè lên video (Overlay)")
        
        self.outro_text_font = tk.StringVar(value="Arial (Mặc định)") # New Font Variable
        
        # Color Filters
        self.color_filter = tk.StringVar(value="Gốc (None)")
        
        # Sticker / Watermark - NEW: Support multiple stickers
        self.stickers_list = []  # List of dicts: [{'path': str, 'pos': str, 'scale': float, 'x': float, 'y': float}, ...]
        
        # Legacy single sticker vars (kept for UI compatibility)
        self.enable_sticker = tk.BooleanVar(value=0)
        self.sticker_path = tk.StringVar(value="")
        self.sticker_pos = tk.StringVar(value="Góc phải dưới")
        self.sticker_scale = tk.DoubleVar(value=0.2)
        
        # Sticker Drag Position (NEW - for interactive drag)
        self.sticker_drag_x = tk.DoubleVar(value=0.85)  # Normalized position (0-1)
        self.sticker_drag_y = tk.DoubleVar(value=0.85)  # Normalized position (0-1)
        self.sticker_dragging = False
        self.dragging_sticker_index = -1  # Which sticker is being dragged
        

    def setup_layout(self):
        """Setup the main 3-column layout (Left: Files, Middle: Preview, Right: Inspector)"""
        # 1. Header
        self.create_header()
        
        # Main Container
        # Use transparent fg_color so it takes root bg
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- LEFT PANEL: FILES ---
        left_frame = ctk.CTkFrame(main_container, width=220, corner_radius=10)  # Reduced from 250
        left_frame.pack(side="left", fill="y", padx=(0, 5), pady=0)
        left_frame.pack_propagate(False) # Enforce width
        
        self.setup_media_panel(left_frame)
        
        # --- MIDDLE PANEL: PREVIEW (LARGER) ---
        middle_frame = ctk.CTkFrame(main_container, corner_radius=10)
        middle_frame.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=0)
        
        self.setup_center_panel(middle_frame)
        
        # --- RIGHT PANEL: INSPECTOR ---
        inspector_frame = ctk.CTkFrame(main_container, width=380, corner_radius=10)  # Increased from 320
        inspector_frame.pack(side="right", fill="y", pady=0)
        inspector_frame.pack_propagate(False) # Enforce width
        
        self.setup_inspector_panel(inspector_frame)
        
        # 3. Footer/Status Bar
        self.create_footer()

    def create_header(self):
        """Application Header (Logo, Theme Toggle, Main Actions)"""
        # Header Container
        header = ctk.CTkFrame(self.root, height=60, corner_radius=10)
        header.pack(fill="x", padx=5, pady=(5, 0))
        header.pack_propagate(False)
        
        # Logo/Title
        ctk.CTkLabel(header, text="Video Editor Pro", font=("Segoe UI", 20, "bold"), text_color="#FFFFFF").pack(side="left", padx=20)
        
        # Version Badge
        ver = ctk.CTkLabel(header, text="PRO", font=("Segoe UI", 10, "bold"), fg_color=get_color(COLOR_ACCENT), text_color="black", width=40, corner_radius=5)
        ver.pack(side="left")
        
        # Theme Toggle Button
        # Logic: We use CTk appearance mode now.
        def toggle_theme_ctk():
            current = ctk.get_appearance_mode()
            new_mode = "Light" if current == "Dark" else "Dark"
            ctk.set_appearance_mode(new_mode)
            self.theme_btn.configure(text=f"☀️ Light" if new_mode == "Dark" else "🌙 Dark")
            # Update TTK styles manually
            self.configure_styles()
            # CRITICAL: Update ALL CTk widgets for proper light mode
            self.update_all_widget_colors()
            
        self.theme_btn = ctk.CTkButton(
            header,
            text="☀️ Light",
            font=("Segoe UI", 12),
            fg_color="transparent",
            border_width=1,
            border_color=("gray60", "#555"),
            text_color=("gray10", "gray90"),
            width=80,
            command=toggle_theme_ctk
        )
        self.theme_btn.pack(side="left", padx=20)
        
        # About Button
        ctk.CTkButton(
            header, 
            text="ℹ️ About", 
            font=("Segoe UI", 12),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            width=80,
            hover=False, # Simple text btn style
            command=self.show_about_dialog
        ).pack(side="left", padx=5)
        
        # Stop Button
        self.stop_btn = ctk.CTkButton(header, text="⏹ DỪNG", fg_color=get_color(COLOR_ERROR), hover_color="#c0392b", width=100, command=self.stop_processing, state="disabled")
        self.stop_btn.pack(side="right", padx=(5, 20))
        
        # Export Button
        self.export_btn = ctk.CTkButton(header, text="XUẤT VIDEO / BẮT ĐẦU", fg_color=get_color(COLOR_ACCENT), hover_color="#009688", font=("Segoe UI", 12, "bold"), text_color="black", height=35, command=self.start_processing)
        self.export_btn.pack(side="right", padx=0)


    def setup_media_panel(self, parent):
        """Left Panel: Input files & Drop Zone"""
        # Title
        ctk.CTkLabel(parent, text="Thư viện Media", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Drop Zone
        drop_frame = ctk.CTkFrame(parent, fg_color=get_color(COLOR_BG_SECONDARY), height=100, cursor="hand2", border_width=2, border_color=("gray70", "#444"))
        drop_frame.pack(fill="x", padx=15, pady=(0, 15))
        drop_frame.pack_propagate(False)
        drop_frame.bind("<Button-1>", lambda e: self.browse_files())
        
        lbl_icon = ctk.CTkLabel(drop_frame, text="+", font=("Segoe UI", 32), text_color=get_color(COLOR_ACCENT))
        lbl_icon.place(relx=0.5, rely=0.4, anchor="center")
        lbl_icon.bind("<Button-1>", lambda e: self.browse_files())
        
        lbl_text = ctk.CTkLabel(drop_frame, text="Drop Files Here / Click to Browse", font=("Segoe UI", 12), text_color="gray")
        lbl_text.place(relx=0.5, rely=0.7, anchor="center")
        lbl_text.bind("<Button-1>", lambda e: self.browse_files())
        
        if TKDND_AVAILABLE:
            # Note: For CTk widgets, we might need to access internals or just rely on parent binding if wrapper works.
            # But DropTarget is usually on Tk widget.
            # Let's try registering on the widget itself.
            try:
                drop_frame.drop_target_register(DND_FILES)
                drop_frame.dnd_bind('<<Drop>>', self.on_drop)
            except: pass
        
        # File List
        list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Treeview (Standard Tkinter) - Styled for Dark Mode
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#2B2B2B", 
                        foreground="white", 
                        fieldbackground="#2B2B2B", 
                        borderwidth=0,
                        rowheight=30)
        style.map('Treeview', background=[('selected', get_color(COLOR_ACCENT))], foreground=[('selected', 'black')])
        style.configure("Treeview.Heading", background="#1E1E1E", foreground="white", borderwidth=0, font=("Segoe UI", 10))
        
        columns = ("name", "duration", "resolution", "size")
        self.tree_media = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        self.tree_media.heading("name", text="Tên File")
        self.tree_media.heading("duration", text="Thời lượng")
        # ... other headings done below or auto
        # To avoid re-typing columns config, I'll assume only this block is replaced.
        # But wait, original code had full col config. I should include it.
        self.tree_media.heading("resolution", text="Độ phân giải")
        self.tree_media.heading("size", text="Dung lượng")
        
        self.tree_media.column("name", width=180)
        self.tree_media.column("duration", width=60)
        self.tree_media.column("resolution", width=90)
        self.tree_media.column("size", width=70)
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_media.yview)
        self.tree_media.configure(yscrollcommand=sb.set)
        
        self.tree_media.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        # Bind Selection
        self.tree_media.bind("<<TreeviewSelect>>", self.on_media_select)
        
        # Context Menu
        # Fix TclError: tk.Menu doesn't support tuple colors. Extract it.
        mode = ctk.get_appearance_mode().lower()
        idx = 1 if mode == "dark" else 0
        
        def c(color): return color[idx] if isinstance(color, tuple) else color
        
        bg_menu = c(get_color(COLOR_BG_SECONDARY))
        fg_menu = c(get_color(COLOR_TEXT_PRIMARY))
        acc_menu = c(get_color(COLOR_ACCENT))
        
        self.context_menu = tk.Menu(self.tree_media, tearoff=0, bg=bg_menu, fg=fg_menu, activebackground=acc_menu, activeforeground="black")
        self.context_menu.add_command(label="❌ Xóa khỏi danh sách", command=self.delete_selected_media)
        
        self.tree_media.bind("<Button-3>", self.show_context_menu)
        
        # Toolbar
        toolbar = ctk.CTkFrame(parent, fg_color=get_color(COLOR_BG_PANEL), height=40)
        toolbar.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(toolbar, text="🔄 Làm mới", fg_color=get_color(COLOR_BUTTON_BG), text_color=get_color(COLOR_TEXT_PRIMARY), height=30, command=self.load_file_list).pack(side="left", padx=2, pady=5)
        # ctk.CTkButton(toolbar, text="🗑️ Xóa tất cả", fg_color=get_color(COLOR_BUTTON_BG), text_color=get_color(COLOR_TEXT_PRIMARY), height=30, command=self.clear_all_media).pack(side="right", padx=2, pady=5)
        ctk.CTkButton(toolbar, text="🗑️ Xóa Tất Cả", fg_color=get_color(COLOR_BUTTON_BG), hover_color=get_color(COLOR_ERROR), text_color=get_color(COLOR_TEXT_PRIMARY), height=30, width=80, command=self.delete_all_files_disk).pack(side="right", padx=2, pady=5)

    def show_context_menu(self, event):
        item = self.tree_media.identify_row(event.y)
        if item:
            self.tree_media.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected_media(self):
        selected_items = self.tree_media.selection()
        if selected_items:
            # Unpack items to delete
            self.tree_media.delete(*selected_items)
            # Stop preview if deleted item was playing
            self.stop_preview = True
            
            # Update status
            current_count = len(self.tree_media.get_children())
            self.status_var.set(f"Remaining: {current_count} files")

    def _perform_disk_deletion(self, files_to_delete):
        """Helper to perform safe disk deletion for a list of (item_id, filename) tuples"""
        if not files_to_delete: return

        msg = f"Bạn có chắc chắn muốn xóa vĩnh viễn {len(files_to_delete)} file khỏi ổ cứng không?"
        if len(files_to_delete) == 1:
            msg = f"Bạn có chắc chắn muốn xóa vĩnh viễn file:\n{files_to_delete[0][1]}\nkhỏi ổ cứng không?"
            
        if messagebox.askyesno("Xóa File Gốc", msg):
            # STEP 1: Pause preview first (if using preview_player)
            if hasattr(self, 'preview_player') and self.preview_player:
                self.preview_player.is_paused = True
                self.preview_player.stop_preview = True
            
            # STEP 2: Stop main preview
            self.stop_preview = True
            
            # STEP 3: Increment preview_id to invalidate ALL running preview threads
            self.preview_id += 1
            
            # STEP 4: Clear preview display immediately
            try:
                self.preview_label.configure(image='', text="⏸️ Đang dừng preview để xóa file...")
                self.preview_label.imgtk = None
                self.latest_frame = None
            except: 
                pass
            
            # STEP 5: Force UI update to process the stop signal
            self.root.update()
            
            # STEP 6: Wait for ALL threads to exit with aggressive timeout
            import time
            import gc
            
            start_wait = time.time()
            max_wait = 5.0  # Increased to 5 seconds
            
            print("⏸️ Stopping all preview threads...")
            
            # Keep updating UI and forcing GC while waiting
            while time.time() - start_wait < max_wait:
                # Check if thread is still alive
                if hasattr(self, 'preview_thread') and self.preview_thread and self.preview_thread.is_alive():
                    self.root.update()
                    gc.collect()  # Force GC every iteration
                    time.sleep(0.2)
                else:
                    break  # Thread died, exit early
            
            # STEP 7: Clean up thread reference
            if hasattr(self, 'preview_thread'):
                self.preview_thread = None
            
            # STEP 8: Reset flags
            self.stop_preview = False
            if hasattr(self, 'preview_player') and self.preview_player:
                self.preview_player.is_paused = False
                self.preview_player.stop_preview = False
            
            # STEP 9: Kill ALL FFmpeg processes to release file handles
            print("🔪 Killing FFmpeg processes...")
            try:
                import subprocess
                # Kill all ffmpeg and ffprobe processes
                subprocess.run(['taskkill', '/F', '/IM', 'ffmpeg.exe'], 
                             capture_output=True, timeout=2)
                subprocess.run(['taskkill', '/F', '/IM', 'ffprobe.exe'], 
                             capture_output=True, timeout=2)
                time.sleep(0.5)
            except Exception as e:
                print(f"Warning: Could not kill FFmpeg: {e}")
            
            # STEP 10: AGGRESSIVE garbage collection (multiple passes)
            print("🗑️ Forcing garbage collection...")
            for i in range(5):  # Increased from 3 to 5
                gc.collect()
                time.sleep(0.2)
            
            # STEP 11: Final safety pause
            print("⏳ Waiting for file handles to release...")
            time.sleep(1.0)  # Increased from 0.5s to 1s
            
            # Update UI
            try:
                self.preview_label.configure(text="🗑️ Đang xóa files...")
                self.root.update()
            except:
                pass
            
            try:
                deleted_ids = []
                failed_files = []
                
                for item_id, filename in files_to_delete:
                    path = os.path.join(self.input_dir.get(), filename)
                    
                    # Retry logic in case file is still locking momentarily
                    success_delete = False
                    last_error = None
                    
                    for retry in range(5):
                        try:
                            if os.path.exists(path):
                                os.remove(path)
                                print(f"Deleted: {path}")
                            success_delete = True
                            break # Success
                        except OSError as e:
                            last_error = e
                            time.sleep(0.5) # Wait and retry
                            gc.collect() # Try GC again
                            
                    if success_delete:
                        deleted_ids.append(item_id)
                    else:
                        # If file not found, it's already gone, consider success for UI
                        if not os.path.exists(path):
                            deleted_ids.append(item_id)
                        else:
                            # Track failed files
                            failed_files.append(filename)
                            print(f"Failed to delete {path}: {last_error}")
                
                # Update UI for successfully deleted files
                if deleted_ids:
                    self.tree_media.delete(*deleted_ids)
                    
                    # Update count
                    current = len(self.tree_media.get_children())
                    self.status_var.set(f"Remaining: {current} files")
                
                # Show results
                if failed_files:
                    failed_list = "\n".join([f"• {f}" for f in failed_files[:10]])  # Show max 10
                    if len(failed_files) > 10:
                        failed_list += f"\n... and {len(failed_files) - 10} more"
                    
                    # msg = f"✅ Đã xóa: {len(deleted_ids)} files\n❌ Thất bại: {len(failed_files)} files\n\n"
                    # msg += "Files bị khóa (đang được sử dụng):\n" + failed_list
                    # msg += "\n\n💡 NGUYÊN NHÂN:\n"
                    # msg += "• Windows Explorer đang preview video\n"
                    # msg += "• Windows Search Indexer\n"
                    # msg += "• Antivirus đang scan\n"
                    # msg += "\n💡 GIẢI PHÁP:\n"
                    # msg += "1. Đóng TẤT CẢ Windows Explorer\n"
                    # msg += "2. Tắt preview: View → Options → Always show icons\n"
                    # msg += "3. Chạy lệnh: taskkill /f /im explorer.exe\n"
                    # msg += "4. Thử lại sau 10 giây"
                    
                    # Ask if user wants to retry
                    result = messagebox.askretrycancel("Xóa một phần", msg)
                    if result:  # User clicked Retry
                        # Recursive retry after delay
                        import time
                        time.sleep(2)
                        self._perform_disk_deletion([(None, f) for f in failed_files])
                # else:
                #     messagebox.showinfo("Thành công", f"✅ Đã xóa thành công {len(deleted_ids)} files!")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}\n(File có thể đang mở ở chương trình khác)")

    def delete_selected_file_disk(self):
        """Delete selected files from disk"""
        selected_items = self.tree_media.selection()
        if not selected_items: return
        
        files_to_delete = []
        for item in selected_items:
            try:
                # Get filename from first column
                fname = self.tree_media.item(item)['values'][0]
                files_to_delete.append((item, fname))
            except: pass
            
        self._perform_disk_deletion(files_to_delete)

    def delete_all_files_disk(self):
        """Delete ALL files in the list from disk"""
        all_items = self.tree_media.get_children()
        if not all_items: return
        
        files_to_delete = []
        for item in all_items:
            try:
                fname = self.tree_media.item(item)['values'][0]
                files_to_delete.append((item, fname))
            except: pass
            
        self._perform_disk_deletion(files_to_delete)

    def clear_all_media(self):
        if messagebox.askyesno("Xóa tất cả", "Bạn có muốn xóa toàn bộ danh sách (chỉ xóa khỏi list, không xóa file)?"):
             self.tree_media.delete(*self.tree_media.get_children())


    def setup_center_panel(self, parent):
        """Center Panel: Video Preview + Console Log (Split View)"""
        # We split using grid or pack. Let's use two frames.
        
        # 1. Video Player Area (Top)
        preview_container = ctk.CTkFrame(parent, fg_color="#000000", corner_radius=0)
        preview_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.preview_label = ctk.CTkLabel(preview_container, text="BẤM VÀO VIDEO ĐỂ XEM TRƯỚC", font=("Segoe UI", 14, "bold"), text_color="#555")
        self.preview_label.pack(fill="both", expand=True)
        
        # Bind mouse events for sticker dragging
        # Bind to both outer widget and internal label to ensure we catch events
        def safe_bind(widget, event, handler):
            try:
                widget.bind(event, handler, add="+")
            except: pass
            
        safe_bind(self.preview_label, "<Button-1>", self.on_preview_click)
        safe_bind(self.preview_label, "<B1-Motion>", self.on_preview_drag)
        safe_bind(self.preview_label, "<ButtonRelease-1>", self.on_preview_release)
        
        # Try binding to internal tkinter widget if it exists (CustomTkinter impl detail)
        if hasattr(self.preview_label, "_label"):
            safe_bind(self.preview_label._label, "<Button-1>", self.on_preview_click)
            safe_bind(self.preview_label._label, "<B1-Motion>", self.on_preview_drag)
            safe_bind(self.preview_label._label, "<ButtonRelease-1>", self.on_preview_release)
            
        if hasattr(self.preview_label, "_canvas"):
             safe_bind(self.preview_label._canvas, "<Button-1>", self.on_preview_click)
             safe_bind(self.preview_label._canvas, "<B1-Motion>", self.on_preview_drag)
             safe_bind(self.preview_label._canvas, "<ButtonRelease-1>", self.on_preview_release)
        
        # === VIDEO PLAYER CONTROLS ===
        controls_frame = ctk.CTkFrame(preview_container, fg_color=get_color(COLOR_BG_HEADER), height=60, corner_radius=0)
        controls_frame.pack(fill="x", side="bottom")
        
        # Play/Pause Button
        self.is_paused = False
        self.play_pause_btn = ctk.CTkButton(controls_frame, text="⏸", font=("Segoe UI", 16), 
                                            command=self.toggle_play_pause,
                                            fg_color=get_color(COLOR_BUTTON_BG), text_color=get_color(COLOR_TEXT_PRIMARY), hover_color=get_color(COLOR_ACCENT),
                                            width=40, height=40)
        self.play_pause_btn.pack(side="left", padx=10, pady=10)
        
        # Time Display
        self.time_label = ctk.CTkLabel(controls_frame, text="00:00 / 00:00", text_color=get_color(COLOR_TEXT_SECONDARY), font=("Segoe UI", 12))
        self.time_label.pack(side="left", padx=5)
        
        # Seek Bar (Slider)
        self.seek_var = tk.DoubleVar(value=0)
        self.seek_bar = ctk.CTkSlider(controls_frame, from_=0, to=100, variable=self.seek_var,
                                     command=self.on_seek,
                                     progress_color=get_color(COLOR_ACCENT), button_color=get_color(COLOR_ACCENT),
                                     button_hover_color="white", height=16)
        self.seek_bar.pack(side="left", fill="x", expand=True, padx=10)
        
        # Video state variables
        self.video_total_frames = 0
        self.video_current_frame = 0
        self.video_fps = 24.0
        self.seeking = False
        
        # 2. Console Log Styled (Bottom)
        # Fixed height and disable propagation to prevent window resizing/jittering
        log_frame = ctk.CTkFrame(parent, height=200, corner_radius=0, fg_color="transparent") 
        log_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        log_frame.pack_propagate(False)  # <--- FIX: Prevent auto-resize based on content

        
        # Header for Log
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent", height=30)
        log_header.pack(fill="x", padx=5)
        ctk.CTkLabel(log_header, text="Nhật Ký Xử Lý", font=("Segoe UI", 12, "bold"), text_color=get_color(COLOR_TEXT_SECONDARY)).pack(side="left")
        
        self.progress_percent = ctk.CTkLabel(log_header, text="0%", text_color=get_color(COLOR_ACCENT), font=("Segoe UI", 12, "bold"))
        self.progress_percent.pack(side="right")
        self.progress_label = ctk.CTkLabel(log_header, text="Sẵn sàng", text_color=get_color(COLOR_TEXT_PRIMARY), font=("Segoe UI", 12))
        self.progress_label.pack(side="right", padx=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(log_frame, progress_color=get_color(COLOR_ACCENT), height=10)
        self.progress_bar.pack(fill="x", padx=5, pady=(0, 5))
        self.progress_bar.set(0)
        
        # Console (CTkTextbox)
        self.console = ctk.CTkTextbox(log_frame, fg_color=("gray95", "#111"), text_color=("#008855", "#00FF88"), font=("Consolas", 12), height=150)
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        self.console.configure(state="disabled")


    def setup_inspector_panel(self, parent):
        """Right Panel: Settings (The Inspector) using CTkTabview"""
        tabs = ctk.CTkTabview(parent, corner_radius=10, fg_color=get_color(COLOR_BG_PANEL)) # fg_color matches content bg
        tabs.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create Tabs (Renamed for better fit)
        tabs.add("Video")
        tabs.add("Audio")
        tabs.add("Intro")
        tabs.add("Stickers")
        tabs.add("Config")
        
        # Configure and Populate Tabs
        
        # Tab 1: Video
        video_scroll = ctk.CTkScrollableFrame(tabs.tab("Video"), fg_color="transparent")
        video_scroll.pack(fill="both", expand=True)
        self.create_video_controls(video_scroll)
        
        # Tab 2: Audio
        self.create_audio_controls(tabs.tab("Audio"))
        
        # Tab 3: Intro/Outro - WITH SCROLLABLE FRAME
        intro_scroll = ctk.CTkScrollableFrame(tabs.tab("Intro"), fg_color="transparent")
        intro_scroll.pack(fill="both", expand=True)
        self.create_io_controls(intro_scroll)
        
        # Tab 4: Sticker
        self.create_sticker_controls(tabs.tab("Stickers"))
        
        # Tab 5: Settings
        self.create_settings_controls(tabs.tab("Config"))

    def create_section_label(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=("Segoe UI", 11, "bold"), text_color=get_color(COLOR_TEXT_SECONDARY))
        lbl.configure(fg_color=parent.cget("fg_color"))  # Inherit parent background
        lbl.pack(anchor="w", pady=(15, 5))
        return lbl  # Return for later updates

    # NOTE: create_slider_row is removed/replaced by create_draggable_row, so we skip defining it here.

    def create_combobox_row(self, parent, label, variable, values):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        
        lbl = ctk.CTkLabel(frame, text=label, text_color=get_color(COLOR_TEXT_PRIMARY))
        lbl.configure(fg_color=frame.cget("fg_color"))  # Inherit parent background
        lbl.pack(side="left", padx=5)
        
        cb = ctk.CTkComboBox(frame, variable=variable, values=values, state="readonly", width=160,
                             fg_color=get_color(COLOR_BG_SECONDARY), text_color=get_color(COLOR_TEXT_PRIMARY), 
                             dropdown_fg_color=get_color(COLOR_BG_SECONDARY))
        cb.pack(side="right", padx=5)
        return cb
    
    def create_checkbox(self, parent, label, variable):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=2)
        
        cb = ctk.CTkCheckBox(frame, text=label, variable=variable, 
                             fg_color=get_color(COLOR_ACCENT), hover_color=get_color(COLOR_ACCENT),
                             text_color=get_color(COLOR_TEXT_PRIMARY), onvalue=True, offvalue=False)
        cb.pack(side="left", padx=5)
        
    def create_video_controls(self, parent):
        # We can write directly to parent (which is scrollable frame)
        frame = parent # It's already the frame we want
        
        # 1. Transform
        self.create_section_label(frame, "BIẾN ĐỔI (CHỐNG BẢN QUYỀN)")
        
        # Aspect Ratio & Resize Mode
        ratios = [
            "Giữ nguyên (Original)",
            "9:16 (TikTok/Shorts)",
            "16:9 (YouTube)",
            "1:1 (Vuông/Instagram)",
            "4:3 (Cổ điển)"
        ]
        self.create_combobox_row(frame, "Tỷ lệ khung hình", self.aspect_ratio, ratios)
        
        resize_modes = ["Thêm viền (Fit)", "Lấp đầy (Fill/Crop)"]
        self.create_combobox_row(frame, "Kiểu hiển thị", self.resize_mode, resize_modes)
        
        # SCALE EXPLICATION: CapCut Style
        scale_header = ctk.CTkFrame(frame, fg_color="transparent")
        scale_header.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(scale_header, text="Scale (%)", text_color=get_color(COLOR_TEXT_PRIMARY), font=("Segoe UI", 12, "bold")).pack(side="left")
        
        # Uniform Scale Checkbox
        cb_uniform = ctk.CTkCheckBox(scale_header, text="Uniform scale", variable=self.uniform_scale, 
                                     fg_color=get_color(COLOR_ACCENT), text_color=get_color(COLOR_TEXT_SECONDARY), width=100)
        cb_uniform.pack(side="right")
        
        # Sync logic
        def sync_scale_h(*args):
            if self.uniform_scale.get():
                try: self.scale_h.set(self.scale_w.get())
                except: pass
        self.scale_w.trace_add("write", sync_scale_h)

        # Draw Controls
        self.create_draggable_row(frame, "Width", self.scale_w, 0.1, 5.0, 0.01)
        self.height_row = self.create_draggable_row(frame, "Height", self.scale_h, 0.1, 5.0, 0.01)
        
        # Helper to disable/enable Height row visually
        def update_uniform_visual(*args):
            pass
        self.uniform_scale.trace_add("write", update_uniform_visual)
        
        # --- NEW: CUT & DURATION ---
        self.create_section_label(frame, "CẮT & THỜI LƯỢNG")
        
        # Cut Start
        self.create_draggable_row(frame, "Cắt bỏ đoạn đầu (Giây)", self.start_time, 0, 600, 1)
        ctk.CTkLabel(frame, text="(Nhập số giây muốn cắt bỏ ở đầu video)", font=("Segoe UI", 9, "italic"), text_color=get_color(COLOR_TEXT_SECONDARY)).pack(anchor="w", padx=10, pady=(0, 5))
        
        # Max Duration
        self.create_draggable_row(frame, "Lấy tối đa (Giây, 0=Full)", self.duration, 0, 3600, 10)


        
        # Init Uniform State (After UI creation)
        # We call it slightly delayed or just now
        # other things

        # Other Controls
        self.create_draggable_row(frame, "Tốc độ (Speed)", self.speed_factor, 1.0, 2.0, 0.01, self.enable_speed)
        self.create_checkbox(frame, "Lật ngược (Mirror)", self.mirror_enabled)
        
        # 2. Adjustments
        self.create_section_label(frame, "MÀU SẮC & HIỆU ỨNG")
        
        # Filter Combobox (Restored)
        # Filter Combobox (Restored)
        lbl_filter = ctk.CTkLabel(frame, text="Bộ lọc màu (Filter)", font=("Segoe UI", 11, "bold"), text_color=get_color(COLOR_TEXT_SECONDARY))
        lbl_filter.configure(fg_color=frame.cget("fg_color"))  # Inherit parent background
        lbl_filter.pack(anchor="w", padx=0, pady=(5,0))
        
        filter_vals = [
            "Gốc (None)", 
            "Đen Trắng (B&W)", 
            "Cổ điển (Sepia)", 
            "Ấm áp (Warm)", 
            "Lạnh lẽo (Cold)", 
            "Phim cũ (Vintage)",
            "Rực rỡ (Vivid)",
            "Điện ảnh (Cinematic)",
            "Mộng mơ (Dreamy)",
            "Kịch tính (Dramatic)",
            "Cyberpunk"
        ]
        # Use CTkComboBox (supports themes)
        # Note: variable logic slightly different, supports stringvar
        filter_combo = ctk.CTkComboBox(frame, variable=self.color_filter, values=filter_vals, state="readonly", width=300)
        filter_combo.pack(fill="x", pady=(0, 10))

        self.create_draggable_row(frame, "Làm mờ (Blur)", self.blur_amount, 0, 20, 0.1, self.enable_blur)
        self.create_draggable_row(frame, "Độ sáng (Brightness)", self.brightness, 0.5, 1.5, 0.1, self.enable_brightness)
        self.create_checkbox(frame, "Chế độ Review Phim (Đơn giản)", self.simple_mode)
        
        # Output Folder Section (NEW - Quick Access)
        self.create_section_label(frame, "THƯ MỤC XUẤT VIDEO")
        
        output_frame = ctk.CTkFrame(frame, fg_color=get_color(COLOR_BG_SECONDARY), corner_radius=8)
        output_frame.pack(fill="x", pady=(5, 10))
        
        # Path display
        self.output_path_label = ctk.CTkLabel(
            output_frame, 
            textvariable=self.output_dir,
            font=("Segoe UI", 10),
            text_color=get_color(COLOR_TEXT_SECONDARY),
            anchor="w",
            fg_color="transparent"
        )
        self.output_path_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        # Browse button
        browse_btn = ctk.CTkButton(
            output_frame,
            text="📁 Chọn",
            width=80,
            height=28,
            fg_color=get_color(COLOR_ACCENT),
            hover_color=get_color(COLOR_ACCENT_HOVER),
            text_color=("black", "black"),
            command=self.config_manager.browse_output_dir
        )
        browse_btn.pack(side="right", padx=8, pady=8)

    def _setup_sticker_traces(self):
        """Setup traces to auto-update active sticker data"""
        def update_data(*args):
            if not self.stickers_list: return
            # Update LAST sticker (Active)
            idx = -1
            if idx < len(self.stickers_list):
                self.stickers_list[idx]['pos'] = self.sticker_pos.get()
                self.stickers_list[idx]['scale'] = self.sticker_scale.get()
                self.stickers_list[idx]['x'] = self.sticker_drag_x.get()
                self.stickers_list[idx]['y'] = self.sticker_drag_y.get()
            
        try:
             self.sticker_pos.trace_add("write", update_data)
             self.sticker_scale.trace_add("write", update_data)
             self.sticker_drag_x.trace_add("write", update_data)
             self.sticker_drag_y.trace_add("write", update_data)
        except: pass

    def create_sticker_controls(self, parent):
        """Enhanced Sticker Tab with Built-in Library (CapCut Style)"""
        # Create scrollable container
        container = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Setup Traces for Real-time Update
        self._setup_sticker_traces()
        
        self.create_section_label(container, "STICKER / WATERMARK")
        self.create_checkbox(container, "Thêm Sticker/Logo (Overlay)", self.enable_sticker)
        
        # === STICKER LIBRARY SECTION ===
        # Use CTkFrame to simulate Labelframe
        lib_frame = ctk.CTkFrame(container, border_width=1, border_color=get_color(COLOR_BORDER))
        lib_frame.pack(fill="both", expand=True, pady=(10, 5))
        
        # Title
        ctk.CTkLabel(lib_frame, text="📚 Thư viện Sticker", font=("Segoe UI", 10, "bold"), text_color=get_color(COLOR_ACCENT)).pack(anchor="w", padx=10, pady=(5,0))
        
        # Category Tabs
        category_frame = ctk.CTkFrame(lib_frame, fg_color="transparent")
        category_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(category_frame, text="Danh mục:", text_color=get_color(COLOR_TEXT_SECONDARY), font=("Segoe UI", 9)).pack(side="left", padx=5)
        
        self.sticker_category = tk.StringVar(value="Emoji")
        # Logic done inside refresh_sticker_grid
        
        # Category Selector
        # Just use a combobox for simpler UI in narrow space
        cats = ["All", "Custom", "Emoji", "Watermark"]
        cat_combo = ctk.CTkComboBox(category_frame, variable=self.sticker_category, values=cats, width=150, height=24, command=lambda e: self.refresh_sticker_grid())
        cat_combo.pack(side="left", padx=5)
        
        # Default to All
        self.sticker_category.set("All")
        
        # Grid Container
        self.sticker_grid_frame = ctk.CTkFrame(lib_frame, fg_color="transparent")
        self.sticker_grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Online Search Button
        ctk.CTkButton(lib_frame, text="🔎 Tìm Sticker Online (Giphy)", fg_color=get_color(COLOR_BUTTON_BG), text_color=get_color(COLOR_TEXT_PRIMARY), 
                      command=self.open_online_search_dialog).pack(fill="x", padx=10, pady=10)

        # === STICKER CONTROLS ===
        self.create_section_label(container, "TÙY CHỈNH STICKER")
        ctrl_frame = ctk.CTkFrame(container, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=5, pady=5)
        
        # Scale Slider
        self.create_draggable_row(ctrl_frame, "Cỡ (Scale)", self.sticker_scale, 0.05, 1.0, 0.01)
        
        # Position Grid (3x3)
        lbl_pos = ctk.CTkLabel(ctrl_frame, text="Vị trí:", font=("Segoe UI", 11, "bold"), text_color=get_color(COLOR_TEXT_SECONDARY))
        lbl_pos.pack(anchor="w", padx=5, pady=(5,0))
        
        pos_grid = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        pos_grid.pack(fill="x", padx=5, pady=5)
        
        positions = [
            ("↖", "Top Left"), ("⬆", "Top Center"), ("↗", "Top Right"),
            ("⬅", "Left Center"), ("CTC", "Center"), ("➡", "Right Center"),
            ("↙", "Bottom Left"), ("⬇", "Bottom Center"), ("↘", "Bottom Right")
        ]
        
        for i, (symbol, val) in enumerate(positions):
            r = i // 3
            c = i % 3
            
            def set_pos(v=val):
                self.sticker_pos.set(v)
                # Also reset drag variables to appropriate approximations for smooth transition if they switch to Custom later
                # (Optional, but good for UX)
                
            btn = ctk.CTkButton(pos_grid, text=symbol, width=40, height=30, 
                                fg_color=get_color(COLOR_BUTTON_BG), hover_color=get_color(COLOR_ACCENT),
                                command=set_pos)
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="ew")
            
        pos_grid.grid_columnconfigure((0,1,2), weight=1)
        
        # Initial Load
        self.refresh_sticker_grid()

        # === VIDEO STICKERS LIST ===
        self.create_section_label(container, "DANH SÁCH STICKER TRÊN VIDEO")
        self.video_stickers_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.video_stickers_frame.pack(fill="both", expand=True, pady=5)

    def refresh_sticker_grid(self):
        """Refresh the sticker grid using CTkButton"""
        # Clear existing
        try:
            for widget in self.sticker_grid_frame.winfo_children():
                widget.destroy()
        except: pass
            
        category = self.sticker_category.get()
        
        # Get stickers
        from UI.sticker import get_sticker_library
        library = get_sticker_library()
        
        stickers = []
        print(f"[DEBUG] Refreshing Sticker Grid. Category: '{category}'")
        
        stickers = []
        print(f"[DEBUG] Refreshing Sticker Grid. Category: '{category}'")
        
        if category == "All":
            # Priority Order: Custom -> Emoji -> Watermark
            priority_order = ["Custom", "Emoji", "Watermark"]
            for key in priority_order:
                if key in library.categories:
                    stickers.extend(library.categories[key])
            
            # Add any remaining categories not in priority list
            for key, val in library.categories.items():
                if key not in priority_order:
                    stickers.extend(val)
        else:
            stickers = library.categories.get(category, [])
            
        print(f"[DEBUG] Total stickers found: {len(stickers)}")
        if category == "Reaction":
            # Mock if empty
            if not stickers: stickers = ["wow", "sad", "love"] # Names/Paths
        if category == "Emoji":
            if not stickers: stickers = ["😀", "😂", "🥰", "😎", "🤔"]
        
        if not stickers:
            ctk.CTkLabel(self.sticker_grid_frame, text="Chưa có sticker (Empty)").pack(pady=20)
            return
        
        # Create grid (3 columns)
        cols = 3
        
        for i, sticker_name in enumerate(stickers):
            row = i // cols
            col = i % cols
            
            # Use CTkButton as Sticker Item
            # Determine Image or Text
            btn_text = ""
            btn_image = None
            
            sticker_path = library.get_sticker_path(sticker_name)
            
            if sticker_path and os.path.exists(sticker_path):
                try:
                    from PIL import Image
                    img_pil = Image.open(sticker_path)
                    # Convert to CTkImage
                    btn_image = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(40, 40))
                except:
                    btn_text = sticker_name[:2]
            else:
                # Is Emoji?
                btn_text = sticker_name.split()[0] if " " in sticker_name else sticker_name
            
            # Define click handler
            def on_click(p=sticker_path, t=btn_text):
                # Update sticker path setting
                self.sticker_path.set(p if p else "")
                self.enable_sticker.set(True)
                
                # Add to multiple sticker list
                if p:
                    self.add_sticker_to_canvas(p)
                else:
                    # Emoji handling? Convert emoji to image?
                    pass
            
            btn = ctk.CTkButton(self.sticker_grid_frame, text=btn_text, image=btn_image, 
                                width=60, height=60, fg_color=get_color(COLOR_BUTTON_BG), 
                                hover_color=get_color(COLOR_ACCENT),
                                command=on_click)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
        # Configure columns
        self.sticker_grid_frame.grid_columnconfigure((0, 1, 2), weight=1)
    
    def add_sticker_to_canvas(self, path):
        # Alias for add_sticker_to_video to match my new logic
        self.sticker_path.set(path)
        self.add_sticker_to_video()
    def add_sticker_to_video(self):
        """Add current sticker settings to the video's sticker list"""
        sticker_path = self.sticker_path.get()
        
        print(f"[DEBUG] add_sticker_to_video called. Path: {sticker_path}")
        print(f"[DEBUG] Current stickers_list length BEFORE add: {len(self.stickers_list)}")
        
        if not sticker_path or not os.path.exists(sticker_path):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sticker trước!")
            return
        
        # Create sticker dict
        sticker_data = {
            'path': sticker_path,
            'pos': self.sticker_pos.get(),
            'scale': self.sticker_scale.get(),
            'x': self.sticker_drag_x.get(),
            'y': self.sticker_drag_y.get()
        }
        
        print(f"[DEBUG] Sticker data: {sticker_data}")
        
        # Add to list
        # Debounce/Duplicate Prevention: strict check
        # If this sticker is identical to the last one added, ignore it.
        if self.stickers_list:
             last = self.stickers_list[-1]
             if (last['path'] == sticker_path and 
                 last['pos'] == self.sticker_pos.get() and
                 last['scale'] == self.sticker_scale.get()):
                  print("[DEBUG] Ignored duplicate sticker addition")
                  return

        self.stickers_list.append(sticker_data)
        
        print(f"[DEBUG] Current stickers_list length AFTER add: {len(self.stickers_list)}")
        print(f"[DEBUG] All stickers in list:")
        for i, s in enumerate(self.stickers_list):
            print(f"  [{i}] {os.path.basename(s['path'])}")
        
        # Enable sticker overlay
        self.enable_sticker.set(True)
        
        # Refresh the list display
        self.refresh_video_stickers_list()
        
        # Show success message
        filename = os.path.basename(sticker_path)
        self.log(f"✅ Đã thêm sticker: {filename}")
    
    def refresh_video_stickers_list(self):
        """Refresh the display of stickers added to video"""
        # Clear existing list
        for widget in self.video_stickers_frame.winfo_children():
            widget.destroy()
        
        # Debug log
        print(f"[DEBUG] Refreshing stickers list. Total stickers: {len(self.stickers_list)}")
        
        if not self.stickers_list:
            ctk.CTkLabel(self.video_stickers_frame, text="Chưa có sticker nào trong video", 
                    text_color="#666", font=("Segoe UI", 9)).pack(pady=20)
            return


        for i, sticker in enumerate(self.stickers_list):
            item_frame = ctk.CTkFrame(self.video_stickers_frame, fg_color=get_color(COLOR_BG_SECONDARY))
            item_frame.pack(fill="x", padx=5, pady=2)
            
            # Sticker info
            filename = os.path.basename(sticker['path'])
            if len(filename) > 25:
                filename = filename[:22] + "..."
            
            info_text = f"📌 {filename} | {sticker['pos']} | {int(sticker['scale']*100)}%"
            ctk.CTkLabel(item_frame, text=info_text, text_color=get_color(COLOR_TEXT_PRIMARY), 
                    font=("Segoe UI", 8), anchor="w").pack(side="left", fill="x", expand=True, padx=5, pady=3)
            
            # Delete button
            def make_delete_cmd(index):
                return lambda: self.remove_sticker_from_video(index)
            
            ctk.CTkButton(item_frame, text="🗑️", command=make_delete_cmd(i),
                               fg_color=get_color(COLOR_ERROR), text_color="white", hover_color="#c0392b", width=30, height=20, font=("Segoe UI", 8)).pack(side="right", padx=2)
        
        # Force update
        self.video_stickers_frame.update_idletasks()
    
    def remove_sticker_from_video(self, index):
        """Remove a sticker from the video (not from library)"""
        if 0 <= index < len(self.stickers_list):
            removed = self.stickers_list.pop(index)
            filename = os.path.basename(removed['path'])
            self.log(f"🗑️ Đã xóa sticker khỏi video: {filename}")
            
            # Disable sticker overlay if no stickers left
            if not self.stickers_list:
                self.enable_sticker.set(False)
            
            # Refresh display
            self.refresh_video_stickers_list()

    def open_online_search_dialog(self):
        """Open dialog to search stickers on Giphy"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Tìm Sticker Online (Giphy)")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header, text="🔍 Tìm kiếm Sticker động từ Giphy", 
                     font=("Segoe UI", 12, "bold")).pack(side="top", pady=(0, 5))
        
        # Search Bar
        search_frame = ctk.CTkFrame(header, fg_color="transparent")
        search_frame.pack(fill="x")
        
        search_var = tk.StringVar()
        entry = ctk.CTkEntry(search_frame, textvariable=search_var, font=("Segoe UI", 11), width=400)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        entry.bind("<Return>", lambda e: perform_search())
        entry.focus_set()
        
        btn_search = ctk.CTkButton(search_frame, text="Tìm kiếm", command=lambda: perform_search(), 
                                  fg_color=get_color(COLOR_ACCENT), text_color="black", font=("Segoe UI", 10, "bold"), width=100)
        btn_search.pack(side="right")
        
        # Status Label (Pack FIRST to ensure visibility at bottom)
        status_lbl = ctk.CTkLabel(dialog, text="Nhập từ khóa để tìm kiếm...", text_color=get_color(COLOR_TEXT_SECONDARY), font=("Segoe UI", 9))
        status_lbl.pack(side="bottom", pady=5)
        
        # Results Grid (Scrollable) (Pack LAST to fill remaining space)
        result_container = ctk.CTkScrollableFrame(dialog, label_text="Kết quả tìm kiếm")
        result_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # API Client
        giphy = GiphyAPI()
        
        # Store references to PhotoImages to prevent Garbage Collection
        self.giphy_images = []
        
        def perform_search():
            query = search_var.get().strip()
            if not query: return
            
            # Disable search button
            btn_search.configure(state="disabled")
            status_lbl.configure(text="Đang tìm kiếm... Vui lòng đợi.")
            dialog.update()
            
            # Clear previous results
            for widget in result_container.winfo_children():
                widget.destroy()
            self.giphy_images = []
            
            def search_task():
                print(f"[DEBUG] Search task start: {query}")
                self.root.after(0, lambda: status_lbl.configure(text=f"Đang gọi API... ({query})"))
                
                try:
                    results = giphy.search_stickers(query, limit=20)
                    print(f"[DEBUG] API returned {len(results)} results")
                    
                    if not results:
                        self.root.after(0, lambda: status_lbl.configure(text="Kết quả rỗng (0 items)."))
                        self.root.after(0, lambda: btn_search.configure(state="normal"))
                        return
                        
                    self.root.after(0, lambda: status_lbl.configure(text=f"DEBUG: Tìm thấy {len(results)} kết quả.", text_color="red"))
                    
                    import requests
                    from io import BytesIO
                    from PIL import Image
                    
                    count = 0
                    for i, item in enumerate(results):
                        # Update UI
                        msg = f"DEBUG: Đang tải {i+1}/{len(results)}..."
                        self.root.after(0, lambda m=msg: status_lbl.configure(text=m, text_color="red"))
                        
                        try:
                            resp = requests.get(item['preview_url'], timeout=10)
                            if resp.status_code == 200:
                                data = BytesIO(resp.content)
                                pil_img = Image.open(data)
                                pil_img.load()
                                pil_img.thumbnail((100, 100))
                                final_img = pil_img.copy()
                                
                                def add_ui(p_img, it):
                                    try:
                                        # Save debug image once
                                        if len(self.giphy_images) == 0:
                                            p_img.save("debug_download.png")
                                            print("[DEBUG] Saved debug_download.png")
                                            
                                        # Verify CTkImage
                                        ctk_img = ctk.CTkImage(light_image=p_img, dark_image=p_img, size=(100, 100))
                                        print(f"[DEBUG] Created CTkImage: {type(ctk_img)}")
                                        self.giphy_images.append(ctk_img)
                                        
                                        f = ctk.CTkFrame(result_container, fg_color="transparent")
                                        r, c = divmod(len(self.giphy_images)-1, 4)
                                        f.grid(row=r, column=c, padx=5, pady=5)
                                        print(f"[DEBUG] Frame grid at {r},{c}")
                                        
                                        btn = ctk.CTkButton(f, text="", image=ctk_img, width=100, height=100,
                                                    fg_color=get_color(COLOR_BUTTON_BG), command=lambda: select_sticker(it))
                                        btn.pack()
                                        print(f"[DEBUG] Button packed for {it['title']}")
                                        
                                    except Exception as ex:
                                        status_lbl.configure(text=f"Lỗi UI: {ex}")
                                        print(f"UI Error: {ex}")
                                        import traceback
                                        traceback.print_exc()

                                self.root.after(0, lambda p=final_img, x=item: add_ui(p, x))
                                count += 1
                        except Exception as e:
                            print(f"Download Error: {e}")
                            
                    self.root.after(0, lambda: status_lbl.configure(text=f"DEBUG: Xong! Hiển thị {count} ảnh.", text_color="red"))
                    
                except Exception as e:
                    self.root.after(0, lambda: status_lbl.configure(text=f"Lỗi API: {e}"))
                    print(f"API Error: {e}")
                finally:
                    self.root.after(0, lambda: btn_search.configure(state="normal"))

            # Start thread
            import threading
            threading.Thread(target=search_task, daemon=True).start()
            return # End of perform_search logic

            # End of perform_search logic (Old code removed)
                    
        def select_sticker(item):
            status_lbl.configure(text=f"Đang tải: {item['title']}...")
            dialog.update()
            
            def download_task():
                path = giphy.download_sticker(item['full_url'], item['id'])
                if path:
                    # Update Main UI
                    def update_ui():
                        try:
                            self.sticker_path.set(path)
                            self.enable_sticker.set(True)
                            status_lbl.configure(text=f"✅ Đã thêm: {item['title']}")
                            
                            # Add to sticker library 'Custom' category
                            from UI.sticker import get_sticker_library
                            import os
                            lib = get_sticker_library()
                            filename = os.path.basename(path)
                            lib.add_custom_sticker(path, display_name=filename)
                            
                            # Set category and refresh
                            self.sticker_category.set("Custom")
                            self.refresh_sticker_grid()
                            
                            # Also add directly to video
                            # Check if methods exist
                            if hasattr(self, 'add_sticker_to_canvas'):
                                self.add_sticker_to_canvas(path)
                            elif hasattr(self, 'add_sticker_to_video'):
                                self.add_sticker_to_video()
                        except Exception as e:
                            print(f"UI Update Error: {e}")
                            status_lbl.configure(text=f"Lỗi cập nhật UI: {e}")
                            
                    self.root.after(0, update_ui)
                else:
                    self.root.after(0, lambda: status_lbl.configure(text="Lỗi tải sticker!"))
                    
            threading.Thread(target=download_task, daemon=True).start()

    def create_settings_controls(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=10)
        
        # === OUTPUT DIRECTORY SECTION (NEW) ===
        self.create_section_label(frame, "THƯ MỤC XUẤT VIDEO")
        
        out_frame = ctk.CTkFrame(frame, fg_color="transparent")
        out_frame.pack(fill="x", pady=(0, 15))
        
        # Path Entry/Label (Display only)
        # Using Entry for better look but readonly
        # Path Entry/Label (Display only)
        # Using Entry for better look but readonly
        self.output_path_label = ctk.CTkEntry(out_frame, textvariable=self.output_dir, state="readonly", fg_color=get_color(COLOR_BG_SECONDARY), border_width=0, text_color=get_color(COLOR_TEXT_SECONDARY))
        self.output_path_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Browse Button
        browse_btn = ctk.CTkButton(out_frame, text="📁 Chọn...", width=80, command=self.config_manager.browse_output_dir, fg_color=get_color(COLOR_BUTTON_BG), text_color=get_color(COLOR_TEXT_PRIMARY), hover_color=get_color(COLOR_ACCENT))
        browse_btn.pack(side="right")

        self.create_section_label(frame, "HIỆU SUẤT & CẤU HÌNH")
        self.create_draggable_row(frame, "Số luồng (Song song)", self.num_threads, 1, 16, 1)
        
        # Thread Info Label
        import multiprocessing
        rec_threads = max(1, multiprocessing.cpu_count() // 2)
        ctk.CTkLabel(frame, text=f"* Khuyến nghị: {rec_threads} - {multiprocessing.cpu_count()} luồng tùy máy mạnh/yếu.", 
                 fg_color="transparent", text_color="#666", font=("Segoe UI", 10), justify="left").pack(anchor="w", pady=(0, 10))

        self.create_section_label(frame, "GPU RENDER")
        self.create_checkbox(frame, "Dùng Card Rời (GPU NVENC)", self.use_gpu)
        
        self.create_section_label(frame, "BACKGROUND PROCESSING")
        self.create_checkbox(frame, "Minimize to Tray (Chạy ngầm khi xuất video)", self.enable_minimize_to_tray)
        
        # === CONFIG MANAGEMENT (NEW) ===
        self.create_section_label(frame, "QUẢN LÝ CẤU HÌNH")
        
        # Buttons Container
        config_buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        config_buttons_frame.pack(fill="x", pady=10)
        
        # Reset Button
        ctk.CTkButton(config_buttons_frame, text="🔄 RESET", fg_color=get_color(COLOR_WARNING), text_color="black", hover_color="#FFB74D", width=80,
                      command=self.config_manager.reset_config).pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        # Save Config Button
        ctk.CTkButton(config_buttons_frame, text="💾 LƯU", fg_color=get_color(COLOR_SUCCESS), text_color="black", hover_color="#66BB6A", width=80,
                      command=self.config_manager.save_config).pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        # Load Config Button
        ctk.CTkButton(config_buttons_frame, text="📂 TẢI", fg_color=get_color(COLOR_ACCENT), text_color="black", hover_color="#4DB6AC", width=80,
                      command=self.config_manager.load_config).pack(side="left", fill="x", expand=True)
        
        # Info Label
        ctk.CTkLabel(frame, text="* Lưu/Tải cấu hình để sử dụng lại các thiết lập yêu thích", 
                 fg_color="transparent", text_color="#666", font=("Segoe UI", 10), justify="left").pack(anchor="w", pady=(0, 5))

    def create_audio_controls(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=10)
        
        # Audio
        self.create_section_label(frame, "AUDIO EFFECTS")
        self.create_draggable_row(frame, "Volume Boost", self.volume_boost, 1.0, 3.0, 0.1)
        self.create_draggable_row(frame, "Bass Boost", self.bass_boost, 0, 20, 1)
        
        # Subtitles (Divider)
        ctk.CTkFrame(frame, height=2, fg_color=get_color(COLOR_BORDER)).pack(fill="x", pady=15)
        
        # Subtitles
        self.create_section_label(frame, "AUTO SUBTITLES")
        self.create_checkbox(frame, "Enable Subtitles (Whisper AI)", self.enable_subtitles)
        
        # Language Selection (NEW)
        lang_frame = ctk.CTkFrame(frame, fg_color="transparent")
        lang_frame.pack(fill="x", pady=(5, 5))
        
        lang_lbl = ctk.CTkLabel(lang_frame, text="Ngôn ngữ / Language:", font=("Segoe UI", 11), text_color=get_color(COLOR_TEXT_PRIMARY))
        lang_lbl.configure(fg_color=lang_frame.cget("fg_color"))  # Inherit parent background
        lang_lbl.pack(side="left", padx=(0, 10))
        
        lang_dropdown = ctk.CTkComboBox(
            lang_frame,
            variable=self.subtitle_language,
            values=["auto (Tự động)", "vi (Tiếng Việt)", "en (English)", "ja (日本語)", "ko (한국어)", "zh (中文)"],
            width=200,
            state="readonly"
        )
        lang_dropdown.pack(side="left")
        
        ctk.CTkLabel(frame, text="* Sử dụng OpenAI Whisper (Small Model)\n* Tự động nhận dạng ngôn ngữ và tạo phụ đề chính xác >95%", 
                            fg_color="transparent", text_color="#666", font=("Segoe UI", 10), justify="left").pack(anchor="w", pady=5)
        
        # Subtitle Black Bar (NEW)
        self.create_section_label(frame, "THANH ĐEN PHỤ ĐỀ")
        self.create_checkbox(frame, "Thêm thanh đen phía dưới (Subtitle Bar)", self.enable_subtitle_bar)
        
        ctk.CTkLabel(frame, text="* Tạo thanh đen ở dưới video để phụ đề dễ đọc hơn", 
                            fg_color="transparent", text_color="#666", font=("Segoe UI", 10), justify="left").pack(anchor="w", pady=(0, 5))
        
        self.create_draggable_row(frame, "Chiều cao thanh đen (px)", self.subtitle_bar_height, 40, 400, 10)

    def create_io_controls(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=10)
        
        # INTRO Section
        self.create_section_label(frame, "INTRO")
        self.create_checkbox(frame, "Enable Intro", self.enable_intro)
        
        # Intro File Display
        intro_display_frame = ctk.CTkFrame(frame, fg_color=get_color(COLOR_BG_SECONDARY), height=35)
        intro_display_frame.pack(fill="x", pady=(5, 5))
        intro_display_frame.pack_propagate(False) 
        
        self.intro_file_label = ctk.CTkLabel(intro_display_frame, text="📁 Chưa chọn file", 
                                          fg_color="transparent", text_color=get_color(COLOR_TEXT_SECONDARY), font=("Segoe UI", 11), 
                                          anchor="w")
        self.intro_file_label.pack(side="left", fill="x", expand=True, padx=10)
        
        ctk.CTkButton(frame, text="Select Intro", fg_color=get_color(COLOR_BUTTON_BG), text_color=get_color(COLOR_TEXT_PRIMARY), hover_color=get_color(COLOR_ACCENT), height=28, width=100,
                  command=lambda: self.browse_io(self.intro_path, self.intro_file_label)).pack(anchor="e", pady=2)
        
        # Separator        
        ctk.CTkFrame(frame, height=2, fg_color=get_color(COLOR_BORDER)).pack(fill="x", pady=15)

        # OUTRO Section
        self.create_section_label(frame, "OUTRO")
        self.create_checkbox(frame, "Enable Outro", self.enable_outro)
        
        # Outro File Display
        outro_display_frame = ctk.CTkFrame(frame, fg_color=get_color(COLOR_BG_SECONDARY), height=35)
        outro_display_frame.pack(fill="x", pady=(5, 5))
        outro_display_frame.pack_propagate(False)
        
        self.outro_file_label = ctk.CTkLabel(outro_display_frame, text="📁 Chưa chọn file", 
                                          fg_color="transparent", text_color=get_color(COLOR_TEXT_SECONDARY), font=("Segoe UI", 11), 
                                          anchor="w")
        self.outro_file_label.pack(side="left", fill="x", expand=True, padx=10)
        
        ctk.CTkButton(frame, text="Select Outro", fg_color=get_color(COLOR_BUTTON_BG), text_color=get_color(COLOR_TEXT_PRIMARY), hover_color=get_color(COLOR_ACCENT), height=28, width=100,
                  command=lambda: self.browse_io(self.outro_path, self.outro_file_label)).pack(anchor="e", pady=2)
                  
        # TEXT OUTRO Section
        ctk.CTkFrame(frame, height=2, fg_color=get_color(COLOR_BORDER)).pack(fill="x", pady=15)
        
        self.create_section_label(frame, "TEXT OUTRO (CUỐI VIDEO)")
        self.create_checkbox(frame, "Hiển thị Text cuối video", self.enable_outro_text)
        
        # Duration selection
        dur_frame = ctk.CTkFrame(frame, fg_color="transparent")
        dur_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(dur_frame, text="Thời lượng (giây cuối):", text_color=get_color(COLOR_TEXT_PRIMARY), font=("Segoe UI", 11)).pack(side="left", padx=5)
        
        def update_dur(val):
            try: self.outro_text_duration.set(int(val))
            except: pass
            
        dur_cb = ctk.CTkComboBox(dur_frame, values=["5", "10", "15", "20", "30"], 
                                width=80, state="readonly",
                                command=update_dur)
        dur_cb.set(str(self.outro_text_duration.get()))
        dur_cb.pack(side="left", padx=5)
        
        # Text Content
        ctk.CTkLabel(frame, text="Nội dung hiển thị:", text_color=get_color(COLOR_TEXT_PRIMARY), font=("Segoe UI", 11)).pack(anchor="w", padx=5, pady=(5,0))
        
        txt_box = ctk.CTkTextbox(frame, height=80, fg_color=get_color(COLOR_BG_SECONDARY), text_color=get_color(COLOR_TEXT_PRIMARY), font=("Segoe UI", 12))
        txt_box.pack(fill="x", padx=5, pady=5)
        
        # Bind text changes
        def on_text_change(event=None):
            self.outro_text_content.set(txt_box.get("1.0", "end-1c"))
            
        txt_box.bind("<KeyRelease>", on_text_change)
        
        # Load initial value (if any loaded from config)
        if self.outro_text_content.get():
            txt_box.insert("1.0", self.outro_text_content.get())
        
        # Customization Options (NEW)
        custom_frame = ctk.CTkFrame(frame, fg_color="transparent")
        custom_frame.pack(fill="x", padx=5, pady=5)
        
        # Style Selection (Append vs Overlay)
        self.create_combobox_row(custom_frame, "Kiểu hiển thị:", self.outro_text_style,
                                ["Màn hình đen (Append)", "Đè lên video (Overlay)"])
        
        # Font Selection (NEW)
        font_options = ["Arial (Mặc định)", "Segoe UI", "Times New Roman", "Tahoma", "Verdana", "Impact"]
        self.create_combobox_row(custom_frame, "Font:", self.outro_text_font, font_options)

        # Font Size - Changed to Slider for better control
        self.create_draggable_row(custom_frame, "Font Size:", self.outro_text_font_size, 10, 300, 5)
        
        # Font Color
        self.create_combobox_row(custom_frame, "Text Color:", self.outro_text_font_color,
                                ["white", "black", "red", "blue", "green", "yellow", "cyan", "magenta"])
        
        # Background
        self.create_combobox_row(custom_frame, "Background:", self.outro_text_bg_color,
                                ["black", "white", "transparent", "#1a1a1a", "#333333"]) # Changed 'gradient' to 'transparent' for clarity
        
        # Text Box Checkbox (NEW)
        self.create_checkbox(custom_frame, "Hiển thị khung đen (Text Box)", self.outro_text_box)
        
        # Box Padding (Visible only if box is checked? Or just always visible but disabled?)
        # Let's show it below checkbox
        self.create_draggable_row(custom_frame, "Khoảng cách (Padding):", self.outro_text_box_padding, 0, 100, 5)
        
        # Position
        self.create_combobox_row(custom_frame, "Position:", self.outro_text_position,
                                ["center", "top", "bottom"])
        
        # Animation
        self.create_combobox_row(custom_frame, "Animation:", self.outro_text_animation,
                                ["none", "fade", "slide_up", "slide_down"])
        
        # PREVIEW CANVAS (NEW - Realtime)
        preview_label = ctk.CTkLabel(frame, text="Preview:", text_color=get_color(COLOR_TEXT_PRIMARY), 
                                     font=("Segoe UI", 11, "bold"))
        preview_label.pack(anchor="w", padx=5, pady=(10, 5))
        
        # Preview canvas
        preview_canvas = ctk.CTkLabel(frame, text="", width=300, height=450, 
                                     fg_color=get_color(COLOR_BG_SECONDARY))
        preview_canvas.pack(padx=5, pady=5)
        
        # Store reference for updates
        self.outro_preview_canvas = preview_canvas
        self.outro_preview_image = None
        
        # Update preview function
        def update_outro_preview():
            try:
                from utils.text_outro_preview import generate_text_outro_preview
                from PIL import ImageTk
                
                # Get current settings
                text = txt_box.get("1.0", "end-1c").strip()
                if not text:
                    text = "Preview text..."
                
                # Generate preview
                pil_img = generate_text_outro_preview(
                    text=text,
                    width=300,
                    height=450,
                    font_size=int(self.outro_text_font_size.get() * 0.5),  # Scale back to 0.5 for larger preview
                    font_color=self.outro_text_font_color.get(),
                    bg_color=self.outro_text_bg_color.get(),
                    position=self.outro_text_position.get(),
                    draw_box=self.outro_text_box.get(),
                    box_padding=self.outro_text_box_padding.get(),
                    font_name=self.outro_text_font.get()
                )
                
                # Convert to CTkImage
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(300, 450))
                
                # Update canvas
                self.outro_preview_canvas.configure(image=ctk_img)
                self.outro_preview_image = ctk_img  # Keep reference
                
            except Exception as e:
                print(f"Preview update error: {e}")
        
        # Bind updates to all settings
        txt_box.bind("<KeyRelease>", lambda e: update_outro_preview())
        self.outro_text_font.trace_add("write", lambda *args: update_outro_preview())
        self.outro_text_font_size.trace_add("write", lambda *args: update_outro_preview())
        self.outro_text_font_color.trace_add("write", lambda *args: update_outro_preview())
        self.outro_text_bg_color.trace_add("write", lambda *args: update_outro_preview())
        self.outro_text_position.trace_add("write", lambda *args: update_outro_preview())
        # self.outro_text_position trace removed here (duplicate)
        self.outro_text_box.trace_add("write", lambda *args: update_outro_preview())
        self.outro_text_box_padding.trace_add("write", lambda *args: update_outro_preview())
        
        # Initial preview
        self.root.after(500, update_outro_preview)

    def create_draggable_row(self, parent, label, variable, min_val, max_val, step, checkbox_var=None):
        """Create a row with Label, optional Checkbox, and Draggable Value + Slider + +/- Buttons (CTk Version)"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=4)
        
        # 1. Left side: Checkbox (optional) + Label
        left_frame = ctk.CTkFrame(frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x")
        
        # Checkbox
        if checkbox_var:
            chk = ctk.CTkCheckBox(left_frame, text="", variable=checkbox_var, width=20, 
                                  fg_color=get_color(COLOR_ACCENT), hover_color=get_color(COLOR_ACCENT))
            chk.pack(side="left")
            
        # Label
        lbl = ctk.CTkLabel(left_frame, text=label, text_color=get_color(COLOR_TEXT_PRIMARY), font=("Segoe UI", 11))
        lbl.configure(fg_color=left_frame.cget("fg_color"))  # Inherit parent background
        lbl.pack(side="left", padx=(0, 5))
        
        # 2. Right side: -/+ Buttons + Draggable Value + Slider
        right_frame = ctk.CTkFrame(frame, fg_color="transparent")
        right_frame.pack(side="right", fill="x", expand=True)
        
        # Draggable Value Label (The "Scrubby" part)
        val_lbl = DraggableValueLabel(right_frame, variable, min_val, max_val, step, 
                                      fg_color=get_color(COLOR_BG_SECONDARY), text_color=get_color(COLOR_ACCENT), width=60, corner_radius=5)
        val_lbl.pack(side="right", padx=(5, 0))
        
        # + Button (Increase)
        def increment():
            current = variable.get()
            new_val = min(max_val, current + step)
            variable.set(new_val)
        
        plus_btn = ctk.CTkButton(right_frame, text="+", width=30, height=24, 
                                 fg_color=get_color(COLOR_ACCENT), hover_color=get_color(COLOR_ACCENT_HOVER),
                                 font=("Segoe UI", 14, "bold"), command=increment)
        plus_btn.pack(side="right", padx=(3, 0))
        
        # - Button (Decrease)
        def decrement():
            current = variable.get()
            new_val = max(min_val, current - step)
            variable.set(new_val)
        
        minus_btn = ctk.CTkButton(right_frame, text="-", width=30, height=24,
                                  fg_color=get_color(COLOR_ACCENT), hover_color=get_color(COLOR_ACCENT_HOVER),
                                  font=("Segoe UI", 14, "bold"), command=decrement)
        minus_btn.pack(side="right", padx=(3, 0))
        
        # Slider
        s = ctk.CTkSlider(right_frame, from_=min_val, to=max_val, variable=variable, 
                          progress_color=get_color(COLOR_ACCENT), button_color=get_color(COLOR_ACCENT), hover=False, height=16)
        s.pack(side="right", fill="x", expand=True, padx=(0, 3))
        
        # Enable/Disable logic
        if checkbox_var:
            def update_state(*args):
                state = 'normal' if checkbox_var.get() else 'disabled'
                s.configure(state=state)
                plus_btn.configure(state=state)
                minus_btn.configure(state=state)
                
                if state == 'normal':
                    val_lbl.configure(text_color=get_color(COLOR_ACCENT))
                else:
                    val_lbl.configure(text_color="gray")
            
            checkbox_var.trace_add("write", update_state)
            
        return frame


    def create_footer(self):
        footer = ctk.CTkFrame(self.root, height=30, fg_color="#1a1a1a", corner_radius=0)
        footer.pack(fill="x")
        
        self.status_var = tk.StringVar(value="Ready")
        ctk.CTkLabel(footer, textvariable=self.status_var, font=("Segoe UI", 10), text_color="gray").pack(side="left", padx=10)
        
        ctk.CTkLabel(footer, text="© 2026 Admin - Video Editor Pro", font=("Segoe UI", 10), text_color="#444").pack(side="right", padx=10)

    # --- CONFIG MANAGEMENT METHODS (Moved to UI/modules/config_manager.py) ---
    # init_settings_vars, reset_config, save_config, load_config 
    # browse_output_dir, auto_save_config, auto_load_config
    


    

    
    def browse_output_dir(self):
        """Open dialog to select output directory"""
        path = filedialog.askdirectory(
            title="Chọn Thư Mục Xuất Video",
            initialdir=self.output_dir.get()
        )
        if path:
            self.output_dir.set(path)
            self.auto_save_config()  # Auto-save immediately
            self.log(f"📂 Đã thay đổi thư mục xuất: {path}")


    

    
    def open_online_search_dialog(self):
        """Open dialog to search stickers on Giphy (CTk Version)"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Tìm Sticker Online (Giphy)")
        dialog.geometry("720x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        ctk.CTkLabel(dialog, text="🔍 Tìm kiếm Sticker động từ Giphy", font=("Segoe UI", 16, "bold"), text_color="white").pack(pady=(15, 10))
        
        # Search Bar
        search_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        search_frame.pack(fill="x", padx=15)
        
        search_var = tk.StringVar()
        entry = ctk.CTkEntry(search_frame, textvariable=search_var, placeholder_text="Nhập từ khóa (vd: cat, fire, wow)...", height=35)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        
        btn_search = ctk.CTkButton(search_frame, text="Tìm kiếm", height=35, fg_color="#9C27B0", hover_color="#7B1FA2",
                                   command=lambda: perform_search())
        btn_search.pack(side="right")
        
        entry.bind("<Return>", lambda e: perform_search())
        entry.focus_set()
        
        # Results Grid (Scrollable)
        result_container = ctk.CTkScrollableFrame(dialog, label_text="Kết quả tìm kiếm")
        result_container.configure(fg_color=get_color(COLOR_BG_SECONDARY))  # Use theme color
        result_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Status Label
        status_lbl = ctk.CTkLabel(dialog, text="Sẵn sàng tìm kiếm", text_color="gray")
        status_lbl.pack(side="bottom", pady=5)
        
        # API Client Import
        try:
            from utils.giphy_api import GiphyAPI
        except ImportError:
            # Mock or alert if missing
            status_lbl.configure(text="Lỗi: Module giphy_api không tìm thấy")
            return

        giphy = GiphyAPI()
        
        # Store references to PhotoImages to prevent Garbage Collection
        self.giphy_images = []
        
        def perform_search():
            query = search_var.get().strip()
            if not query: return
            
            status_lbl.configure(text=f"Đang tìm '{query}'...", text_color=get_color(COLOR_ACCENT))
            # Clear old results
            for w in result_container.winfo_children():
                w.destroy()
            self.giphy_images.clear()
            
            # Run in thread
            threading.Thread(target=search_task, args=(query,), daemon=True).start()
            
        def search_task(query):
            results = giphy.search_stickers(query, limit=24)
            
            if not results:
                self.root.after(0, lambda: status_lbl.configure(text="Không tìm thấy kết quả nào.", text_color="orange"))
                return
            
            # Download thumbnails
            self.root.after(0, lambda: status_lbl.configure(text=f"Đang tải {len(results)} hình ảnh..."))
            
            # Load images logic
            load_images_bg(results)
            
        def load_images_bg(results):
            # We process images one by one or in batch
            from PIL import Image, ImageTk
            import requests
            from io import BytesIO
            
            row = 0
            col = 0
            cols = 4
            
            # Config grid
            for i in range(cols):
                result_container.columnconfigure(i, weight=1)
            
            for i, item in enumerate(results):
                try:
                    # Get url from GiphyAPI result structure
                    url = item.get('preview_url') # Changed from direct dict access as GiphyAPI pre-processes it
                    if not url: 
                        # Fallback if raw dict passed
                        url = item.get('images', {}).get('fixed_height_small', {}).get('url')
                    
                    if not url: continue
                    
                    response = requests.get(url)
                    img_data = BytesIO(response.content)
                    pil_img = Image.open(img_data)
                    pil_img.load()
                    
                    # Pass to UI thread
                    self.root.after(0, lambda img=pil_img, it=item, r=row, c=col: show_img(img, it, r, c))
                    
                    col += 1
                    if col >= cols:
                        col = 0
                        row += 1
                        
                except Exception as e:
                    print(f"Error loading sticker thumb: {e}")
            
            def update_finish_status():
                try:
                    if status_lbl.winfo_exists():
                        status_lbl.configure(text="Hoàn tất!", text_color=get_color(COLOR_SUCCESS))
                except: pass

            self.root.after(0, update_finish_status)

        def show_img(pil_img, item, r, c):
            try:
                if not result_container.winfo_exists(): return
            except: return
            
            # Create CTkImage for high quality on main thread
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(80, 80))
            self.giphy_images.append(ctk_img) # Keep ref
            
            try:
                btn = ctk.CTkButton(result_container, image=ctk_img, text="", width=90, height=90,
                                    fg_color=COLOR_BG_MAIN, hover_color=get_color(COLOR_ACCENT),
                                    command=lambda: select_sticker(item))
                btn.grid(row=r, column=c, padx=5, pady=5)
            except Exception as e:
                print(f"Error showing sticker thumb: {e}")
            
        def select_sticker(item):
            # Download full size logic
            # Download full size logic
            url = item.get('full_url')
            if not url:
                url = item.get('images', {}).get('original', {}).get('url')
            
            if not url: return
            
            status_lbl.configure(text="Đang tải xuống sticker gốc...", text_color=get_color(COLOR_ACCENT))
            threading.Thread(target=lambda: download_task(url), daemon=True).start()
            
        def download_task(url):
             import requests
             import time
             try:
                response = requests.get(url)
                if response.status_code == 200:
                    # Save to temp
                    filename = f"giphy_{int(time.time())}.gif"
                    
                    # Ensure temp dir exists. Actually we should save to sticker library or temp.
                    # Let's save to 'stickers/downloaded'
                    from UI.sticker import get_sticker_library
                    lib = get_sticker_library()
                    # Use lib.stickers_dir (Path object)
                    save_path = os.path.join(lib.stickers_dir, filename)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    
                    # Update UI
                    self.root.after(0, lambda: update_ui_success(save_path))
             except Exception as e:
                 print(e)
                 self.root.after(0, lambda: status_lbl.configure(text="Lỗi tải xuống.", text_color="red"))

        def update_ui_success(path):
            # Register with library
            from UI.sticker import get_sticker_library
            lib = get_sticker_library()
            lib.add_custom_sticker(path)
            
            # Refresh sticker dropdown if it exists
            # We need to refresh self.sticker_dropdown values
            if hasattr(self, 'sticker_dropdown'):
                stickers = lib.get_all_stickers()
                display_list = []
                for cat, items in stickers.items():
                    # Prefix category for clarity (optional, or just list names)
                    # Current impl likely just lists names. 
                    # Let's just update based on current category selection logic
                    pass 
                
                # Force refresh of the stickers list variable
                # self.update_sticker_list() # If such method exists
                # Or just manually:
                current_cat = self.sticker_category_var.get()
                if current_cat == "Custom" or current_cat == "Giphy": # If we add Giphy cat later
                     self.sticker_dropdown.configure(values=stickers.get("Custom", []))
                     self.sticker_dropdown.set(os.path.basename(path))
                     self.sticker_path.set(path)
            
            status_lbl.configure(text="Đã thêm vào thư viện! ✅", text_color=get_color(COLOR_SUCCESS))
            # try:
            #     destroy_dialog()
            # except: pass
            
            # Select it
            self.sticker_category.set("All") 
            print(f"[DEBUG] Refreshing sticker grid with ALL stickers...")
            self.refresh_sticker_grid()
            print(f"[DEBUG] Refresh complete.")
            
            # Auto-add to video canvas immediately
            self.add_sticker_to_canvas(path)
            
            # Allow user to edit immediately
            self.enable_sticker.set(True)
            
            status_lbl.configure(text="Đã thêm vào Video! ✅", text_color=get_color(COLOR_SUCCESS))

        def destroy_dialog():
            dialog.destroy()

    # --- Logic Methods (Simplified using utils) ---


    
    def log(self, message):
        """Thread-safe logging"""
        def _write():
            self.console.configure(state="normal")
            self.console.insert("end", f"> {message}\n")
            self.console.see("end")
            self.console.configure(state="disabled")
        self.root.after(0, _write)

    def add_file_to_tree(self, file_path):
        """Helper to add a single file to the treeview if not already present"""
        filename = os.path.basename(file_path)
        
        # Check duplicates in UI
        for item in self.tree_media.get_children():
            if self.tree_media.item(item)['values'][0] == filename:
                return # Already exists
        
        try:
            # Get file size
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Get video info (duration, resolution, fps)
            duration_str = "--:--"
            resolution_str = "---"
            
            try:
                video_info = get_video_info(file_path)
                if video_info:
                    # Duration
                    duration = video_info.get('duration', 0)
                    if duration > 0:
                        mins = int(duration // 60)
                        secs = int(duration % 60)
                        duration_str = f"{mins:02d}:{secs:02d}"
                    
                    # Resolution
                    width = video_info.get('width', 0)
                    height = video_info.get('height', 0)
                    if width and height:
                        resolution_str = f"{width}x{height}"
            except:
                pass  # If video info fails, use default values
            
            # Insert with all columns
            self.tree_media.insert("", "end", values=(
                filename, 
                duration_str,
                resolution_str,
                f"{size_mb:.1f} MB"
            ))
        except OSError:
            pass

    def load_file_list(self):
        """Refresh content from Input Directory"""
        self.tree_media.delete(*self.tree_media.get_children())
        files = get_video_files(self.input_dir.get())
        for f in files:
            file_path = os.path.join(self.input_dir.get(), f)
            self.add_file_to_tree(file_path)
        self.status_var.set(f"Loaded {len(files)} files")

    def clear_file_list(self):
        # Legacy stub
        self.load_file_list()

    def browse_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])
        if files:
            import shutil
            target_dir = self.input_dir.get()
            added_count = 0
            for f in files:
                name = os.path.basename(f)
                dest = os.path.join(target_dir, name)
                
                # Copy logic (Only if not exist to save time/disk)
                if not os.path.exists(dest):
                    try:
                        shutil.copy2(f, dest)
                    except: pass
                
                # Add to UI directly without reloading everything
                self.add_file_to_tree(dest)
                added_count += 1
            
            self.status_var.set(f"Added {added_count} files")

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        import shutil
        target_dir = self.input_dir.get()
        added_count = 0
        for f in files:
            if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                name = os.path.basename(f)
                dest = os.path.join(target_dir, name)
                
                if not os.path.exists(dest):
                    try:
                        shutil.copy2(f, dest)
                    except: pass
                
                # Add to UI directly
                self.add_file_to_tree(dest)
                added_count += 1
        
        if added_count > 0:
            self.status_var.set(f"Dropped {added_count} files")

    def browse_io(self, var, label_widget=None):
        f = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv;*.webm;*.flv;*.wmv;*.m4v")])
        if f:
            var.set(f)
            # Update label if provided
            if label_widget:
                filename = os.path.basename(f)
                label_widget.configure(text=f"✅ {filename}", text_color="#00FF88")  # Green color for selected file

    def check_updates_bg(self):
        update = check_for_updates()
        if update:
            self.root.after(0, lambda: messagebox.showinfo("Update Available", f"New version {update['version']} is available!"))
    
    # === STICKER DRAG & DROP HANDLERS (NEW) ===
    def on_preview_click(self, event):
        """Handle mouse click on preview - check if clicking on sticker"""
        print(f"[RAW CLICK] Event at: {event.x}, {event.y}")
        if not self.enable_sticker.get():
            return
        
        sticker_path = self.sticker_path.get()
        if not sticker_path or not os.path.exists(sticker_path):
            return
            
        # Get preview label dimensions
        lbl_w = self.preview_label.winfo_width()
        lbl_h = self.preview_label.winfo_height()
        
        # Check if preview image dimensions are available
        if hasattr(self, 'preview_img_w') and self.preview_img_w:
            img_w = self.preview_img_w
            img_h = self.preview_img_h
        else:
            print("[WARNING] preview_img_w missing! Using label dims.")
            img_w = lbl_w
            img_h = lbl_h
            
        if lbl_w <= 1 or lbl_h <= 1:
            return
            
        if img_w <= 0: img_w = 1
        if img_h <= 0: img_h = 1
        
        # Calculate image offset (Centered)
        offset_x = (lbl_w - img_w) // 2
        offset_y = (lbl_h - img_h) // 2
        
        # Convert click to image coordinates
        img_click_x = event.x - offset_x
        img_click_y = event.y - offset_y
        
        # Check bounds (clicking black bars)
        if not (0 <= img_click_x <= img_w and 0 <= img_click_y <= img_h):
            return

        # DEBUG INFO
        print(f"[DEBUG HIT] Event: {event.x},{event.y} | Label: {lbl_w}x{lbl_h} | Img: {img_w}x{img_h} | Offset: {offset_x},{offset_y}")
        print(f"[DEBUG HIT] Click Img: {img_click_x},{img_click_y} | Norm: {click_x:.2f},{click_y:.2f}")
        
        # ... Scale and Pos calc (keep existing) ...
        # Get sticker scale
        sticker_scale = self.sticker_scale.get()
        sticker_w_norm = sticker_scale
        aspect_ratio = img_w / img_h if img_h > 0 else 1.0
        sticker_h_norm = sticker_scale * aspect_ratio
        
        # Calculate ACTUAL sticker position
        sticker_pos = self.sticker_pos.get()
        
        if "Tùy chỉnh" in sticker_pos or "Custom" in sticker_pos:
            sticker_x = self.sticker_drag_x.get()
            sticker_y = self.sticker_drag_y.get()
        else:
            margin_px = 20
            margin_x_norm = margin_px / img_w
            margin_y_norm = margin_px / img_h
            
            # Default: Bottom-Right
            sticker_x = 1 - sticker_w_norm - margin_x_norm
            sticker_y = 1 - sticker_h_norm - margin_y_norm
            
            # Vertical Logic
            if "Top" in sticker_pos or "trên" in sticker_pos:
                sticker_y = margin_y_norm
            elif "Bottom" in sticker_pos or "dưới" in sticker_pos:
                sticker_y = 1 - sticker_h_norm - margin_y_norm
            elif "Center" in sticker_pos or "giữa" in sticker_pos:
                sticker_y = (1 - sticker_h_norm) / 2
                
            # Horizontal Logic
            if "Left" in sticker_pos or "trái" in sticker_pos:
                sticker_x = margin_x_norm
            elif "Right" in sticker_pos or "phải" in sticker_pos:
                sticker_x = 1 - sticker_w_norm - margin_x_norm
            elif "Center" in sticker_pos or "giữa" in sticker_pos:
                sticker_x = (1 - sticker_w_norm) / 2
                
        print(f"[DEBUG HIT] Sticker Target: {sticker_x:.2f},{sticker_y:.2f} Size: {sticker_w_norm:.2f}x{sticker_h_norm:.2f}")

        # Check if click is within sticker bounds
        base_margin = 0.2
        
        # TRY 1: With Calculated Offset (Center)
        hit = False
        
        if (sticker_x - base_margin < click_x < sticker_x + sticker_w_norm + base_margin and
            sticker_y - base_margin < click_y < sticker_y + sticker_h_norm + base_margin):
            hit = True
            print("✅ HIT (Centered Logic)")
        else:
            # TRY 2: Without Offset (Maybe Image Fills?)
            alt_click_x = event.x / img_w
            alt_click_y = event.y / img_h
            
            if (sticker_x - base_margin < alt_click_x < sticker_x + sticker_w_norm + base_margin and
                sticker_y - base_margin < alt_click_y < sticker_y + sticker_h_norm + base_margin):
                hit = True
                print("✅ HIT (Fill Logic - No Offset)")
                # If this hits, it means our offset logic was interfering.
                # Adjust vars to match this logic for this session?
                # Actually, dragging needs to match.
                # Let's set a flag or just proceed.
                click_x, click_y = alt_click_x, alt_click_y
                # Also zero out offsets for drag handler?
                # For now just let it drag.

        if hit:
            self.sticker_dragging = True
            self.preview_label.configure(cursor="fleur")
            self.drag_offset_x = click_x - sticker_x
            self.drag_offset_y = click_y - sticker_y
            
            self.sticker_drag_x.set(sticker_x)
            self.sticker_drag_y.set(sticker_y)
        else:
             print("❌ MISS Both Strategies")
    
    def on_preview_drag(self, event):
        """Handle mouse drag - move sticker"""
        if not self.sticker_dragging:
            return
        
        if not hasattr(self, 'preview_img_w') or not self.preview_img_w:
            return
            
        lbl_w = self.preview_label.winfo_width()
        lbl_h = self.preview_label.winfo_height()
        img_w = self.preview_img_w
        img_h = self.preview_img_h
        
        offset_x = (lbl_w - img_w) // 2
        offset_y = (lbl_h - img_h) // 2
        
        # Convert click to image coordinates
        img_drag_x = event.x - offset_x
        img_drag_y = event.y - offset_y
        
        # Normalize
        drag_x = img_drag_x / img_w
        drag_y = img_drag_y / img_h
        
        # Calculate new sticker position
        new_x = drag_x - self.drag_offset_x
        new_y = drag_y - self.drag_offset_y
        
        # Clamp to bounds (0-1) (Allow slightly out of bounds dragging for edge placement)
        new_x = max(-0.1, min(1.1, new_x))
        new_y = max(-0.1, min(1.1, new_y))
        
        # Update position
        self.sticker_drag_x.set(new_x)
        self.sticker_drag_y.set(new_y)
        
        # Force Custom mode
        self.sticker_pos.set("Tùy chỉnh (Custom)")
        
    def on_preview_release(self, event):
        """Handle mouse release - stop dragging"""
        self.sticker_dragging = False
        self.preview_label.configure(cursor="arrow")

    # === VIDEO PLAYER CONTROLS (NEW) ===
    def toggle_play_pause(self):
        """Toggle video playback pause/resume"""
        self.is_paused = not self.is_paused
        # self.preview_player.is_paused = self.is_paused  # Sync with player (Removed: using internal thread)
        
        if self.is_paused:
            self.play_pause_btn.configure(text="▶")  # Play icon
        else:
            self.play_pause_btn.configure(text="⏸")  # Pause icon
    
    def on_seek(self, value):
        """Handle seek bar movement"""
        if not hasattr(self, 'video_total_frames') or self.video_total_frames == 0:
            return
        
        # Calculate target frame
        seek_percent = float(value) / 100.0
        target_frame = int(seek_percent * self.video_total_frames)
        
        # Set seeking flag and target (sync with player)
        self.seeking = True
        self.seek_target_frame = target_frame
        self.preview_player.seeking = True
        self.preview_player.seek_target_frame = target_frame
        
        # Update time display
        current_time = target_frame / self.video_fps if self.video_fps > 0 else 0
        total_time = self.video_total_frames / self.video_fps if self.video_fps > 0 else 0
        self.time_label.configure(text=f"{self.format_time(current_time)} / {self.format_time(total_time)}")
    
    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def start_processing(self):
        if self.is_processing:
            return
        
        files_items = self.tree_media.get_children()
        if not files_items:
            messagebox.showwarning("Warning", "No media files to process!")
            return
            
        self.is_processing = True
        self.log("🚀 Starting processing batch...")
        
        # Collect settings
        settings = {
            'start_time': self.start_time.get(),
            'duration': self.duration.get(),
            
            'enable_blur': self.enable_blur.get(),
            'blur_amount': self.blur_amount.get(),
            
            'enable_brightness': self.enable_brightness.get(),
            'brightness': self.brightness.get(),
            
            # Scale (New)
            'scale_w': self.scale_w.get(),
            'scale_h': self.scale_h.get(),
            
            'enable_speed': self.enable_speed.get(),
            'speed_factor': self.speed_factor.get(),
            
            'mirror_enabled': self.mirror_enabled.get(),
            'aspect_ratio': self.aspect_ratio.get(),
            'resize_mode': self.resize_mode.get(), # New
            'simple_mode': self.simple_mode.get(),
            'volume_boost': self.volume_boost.get(),
            'bass_boost': self.bass_boost.get(),
            'use_gpu': self.use_gpu.get(),
            'subtitle_font_size': 14, # Default
        
            # Intro / Outro
            'enable_intro': self.enable_intro.get(),
            'intro_path': self.intro_path.get(),
            'enable_outro': self.enable_outro.get(),
            'outro_path': self.outro_path.get(),
            
            # Text Outro (NEW)
            'enable_outro_text': self.enable_outro_text.get(),
            'outro_text_duration': self.outro_text_duration.get(),
            'outro_text_content': self.outro_text_content.get(),
            'outro_text_font': self.outro_text_font.get(),
            'outro_text_font_size': self.outro_text_font_size.get(),
            'outro_text_font_color': self.outro_text_font_color.get(),
            'outro_text_bg_color': self.outro_text_bg_color.get(),
            'outro_text_position': self.outro_text_position.get(),
            'outro_text_animation': self.outro_text_animation.get(),
            'outro_text_box': self.outro_text_box.get(),
            'outro_text_box_padding': self.outro_text_box_padding.get(),
            'outro_text_style': "overlay" if "Overlay" in self.outro_text_style.get() else "append",

            
            # New Features: Filter & Sticker
            'color_filter': self.color_filter.get(),
            
            # Multiple Stickers Support (NEW)
            'stickers_list': self.stickers_list.copy(),  # Pass the list of stickers
            
            # Legacy single sticker (kept for backward compatibility)
            'enable_sticker': self.enable_sticker.get(),
            'sticker_path': self.sticker_path.get(),
            'sticker_pos': self.sticker_pos.get(),
            'sticker_scale': self.sticker_scale.get(),
            'sticker_drag_x': self.sticker_drag_x.get(),
            'sticker_drag_y': self.sticker_drag_y.get(),
            
            # Subtitle Black Bar (NEW)
            'enable_subtitle_bar': self.enable_subtitle_bar.get(),
            'subtitle_bar_height': self.subtitle_bar_height.get(),
        }
        
        # Get files
        files = []
        for item in files_items:
            files.append(self.tree_media.item(item)['values'][0])
        
        # Enable stop button, disable export button
        self.stop_btn.configure(state="normal")
        self.export_btn.configure(state="disabled")
        
        # 🚀 AUTO BACKGROUND PROCESSING (Always enabled)
        # Store files count for notifications
        self.files_to_process = files
        self.total_files_to_process = len(files)
        self.processed_count = 0
        
        # Enable background processing (auto minimize + notifications)
        # enable_background_processing(self)  # DISABLED BY USER REQUEST
        self.log(f"🚀 Bắt đầu xử lý {len(files)} files...")
        
        threading.Thread(target=self.process_queue, args=(files, settings)).start()
    
    def stop_processing(self):
        """Stop ongoing video processing"""
        if not self.is_processing:
            return
        
        # Set stop flag - This triggers the check_stop_signal in video_processor.py
        # which will safely kill the specific FFmpeg process associated with this job.
        self.is_processing = False
        self.log("🛑 Đang dừng quá trình xử lý... (Sending kill signal)")
        
        # Disable button immediately
        self.stop_btn.configure(state="disabled")
        self.status_var.set("Stopping...")
        
        # Force UI update
        self.root.update()
        
        # Note: The actual FFmpeg process kill happens in the background thread
        # within utils/video_processor.py (process_video_with_ffmpeg)
        # by checking the checks_stop_signal callback.
        
        # We don't need to manually run taskkill here anymore, which is safer
        # as it won't kill other unrelated FFmpeg instances.

        # Allow a moment for threads to clean up
        self.root.after(1000, self._finalize_stop)

    def _finalize_stop(self):
         self.log("✅ Đã dừng xử lý.")
         self.export_btn.configure(state="normal")
         self.status_var.set("Stopped")
         self.update_progress(0, 1, "Đã dừng")
         messagebox.showinfo("Đã Dừng", "Quá trình xử lý đã được dừng!")


    def update_progress(self, current, total, filename="", spinner_frame=0):
        """Update progress bar safely (Thread-safe)"""
        def _update():
            # Check if root still exists
            try:
                if not self.root or not self.root.winfo_exists(): return
            except: return

            try:
                # Calculate percentage
                percent = int((current / total) * 100) if total > 0 else 0
                
                # Update progress bar width
                self.progress_bar.place(relwidth=percent/100)
                
                # Update percentage text
                self.progress_percent.configure(text=f"{percent}%")
                
                # Spinner animation (shows activity)
                spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
                spinner_char = spinner[spinner_frame % len(spinner)]
                
                # Update status label
                if current < total:
                    self.progress_label.configure(text=f"{spinner_char} Đang xử lý: {filename} ({current}/{total})")
                    # Change color based on progress
                    if percent < 50:
                        self.progress_bar.configure(progress_color=get_color(COLOR_ACCENT))  # Cyan
                    else:
                        self.progress_bar.configure(progress_color=get_color(COLOR_SUCCESS))  # Green
                else:
                    self.progress_label.configure(text=f"✅ Hoàn tất! ({current}/{total})")
                    self.progress_bar.configure(progress_color=get_color(COLOR_SUCCESS))
            except Exception as e:
                print(f"UI Update Error: {e}")
        
        # Schedule safely
        try:
            if self.root and self.root.winfo_exists():
                self.root.after(0, _update)
        except: pass
    
    def update_progress_percent(self, percent, filename=""):
        """Update progress bar with direct percentage (Thread-safe)"""
        def _update():
            try:
                if not self.root or not self.root.winfo_exists(): return
            except: return

            try:
                # Clamp percent to 0-100
                percent_clamped = max(0, min(100, percent))
                
                # Update progress bar width
                self.progress_bar.place(relwidth=percent_clamped/100)
                
                # Update percentage text
                self.progress_percent.configure(text=f"{percent_clamped}%")
                
                # Update status label
                self.progress_label.configure(text=f"⚡ Đang xử lý: {filename} ({percent_clamped}%)")
                
                # Change color based on progress
                if percent_clamped < 50:
                    self.progress_bar.configure(progress_color=get_color(COLOR_ACCENT))  # Cyan
                else:
                    self.progress_bar.configure(progress_color=get_color(COLOR_SUCCESS))  # Green
            except:
                pass
        
        try:
            if self.root and self.root.winfo_exists():
                self.root.after(0, _update)
        except: pass
    
    def animate_spinner(self, current, total, filename):
        """Animate spinner while processing"""
        if not hasattr(self, '_spinner_frame'):
            self._spinner_frame = 0
        
        self._spinner_frame += 1
        self.update_progress(current, total, filename, self._spinner_frame)
        
        # Continue animation if still processing
        if self.is_processing and current < total:
            self.root.after(100, lambda: self.animate_spinner(current, total, filename))

    
    def process_queue(self, files, settings):
        import concurrent.futures
        
        # Get thread count setting
        max_workers = self.num_threads.get()
        if max_workers < 1: max_workers = 1
        
        self.log(f"🚀 Bắt đầu xử lý với {max_workers} luồng song song...")
        
        total = len(files)
        completed = 0
        success_count = 0
        fail_count = 0
        
        # Reset progress bar
        self.update_progress(0, total, "Đang khởi động...")
        
        # PRE-NORMALIZE INTRO/OUTRO (1 lần duy nhất cho tất cả video)
        normalized_intro = None
        normalized_outro = None
        
        if settings.get('enable_intro') and settings.get('intro_path'):
            self.log("   🔧 Pre-normalizing Intro (1 lần cho tất cả video)...")
            try:
                from utils.video_processor import normalize_segment_for_concat
                normalized_intro = normalize_segment_for_concat(
                    settings['intro_path'], 
                    settings['aspect_ratio'],
                    "intro_shared",
                    log_callback=self.log,
                    use_gpu=settings.get('use_gpu', True)
                )
                if normalized_intro:
                    self.log(f"   ✅ Intro normalized: {normalized_intro}")
                    settings['normalized_intro'] = normalized_intro
                else:
                    self.log("   ⚠️ Intro normalization failed, will skip intro")
                    settings['enable_intro'] = False
            except Exception as e:
                self.log(f"   ⚠️ Intro pre-normalize error: {e}")
                settings['enable_intro'] = False
        
        if settings.get('enable_outro') and settings.get('outro_path'):
            self.log("   🔧 Pre-normalizing Outro (1 lần cho tất cả video)...")
            try:
                from utils.video_processor import normalize_segment_for_concat
                normalized_outro = normalize_segment_for_concat(
                    settings['outro_path'],
                    settings['aspect_ratio'],
                    "outro_shared",
                    log_callback=self.log,
                    use_gpu=settings.get('use_gpu', True)
                )
                if normalized_outro:
                    self.log(f"   ✅ Outro normalized: {normalized_outro}")
                    settings['normalized_outro'] = normalized_outro
                else:
                    self.log("   ⚠️ Outro normalization failed, will skip outro")
                    settings['enable_outro'] = False
            except Exception as e:
                self.log(f"   ⚠️ Outro pre-normalize error: {e}")
                settings['enable_outro'] = False
        
        lock = threading.Lock() # For updating counters safely
        
        def _process_single_file(filename):
            nonlocal completed, success_count, fail_count
            
            # Progress will be updated by FFmpeg callback in real-time
            # No need for initial update here

            
            input_path = os.path.join(self.input_dir.get(), filename)
            output_path = os.path.join(self.output_dir.get(), filename)
            
            # 1. Subtitles
            srt_path = None
            if self.enable_subtitles.get():
                try:
                    # Pre-check for Audio Stream to save time/errors
                    from utils.video_processor import get_video_info
                    v_info = get_video_info(input_path)
                    if not v_info or not v_info.get('has_audio', False):
                        self.log(f"   ⚠️ No audio stream detected. Skipping subtitles for: {filename}")
                        srt_path = None
                    else:
                        self.log(f"   📝 Generating subtitles for: {filename}")
                        
                        # Extract language code from dropdown (e.g., "vi (Tiếng Việt)" -> "vi")
                        lang_str = self.subtitle_language.get()
                        if "auto" in lang_str.lower():
                            language_code = None  # None = Auto-detect
                            self.log(f"   🌐 Language: Auto-detect (Whisper will identify)")
                        else:
                            language_code = lang_str.split()[0] if lang_str else None
                            self.log(f"   🌐 Language: {language_code}")
                        
                        audio_temp = f"temp_audio_{abs(hash(filename))}.wav"
                        from utils.subtitle_generator import extract_audio_from_video, generate_subtitles_with_whisper
                        if extract_audio_from_video(input_path, audio_temp, log_callback=self.log):
                            srt_path = generate_subtitles_with_whisper(
                                audio_temp, 
                                language=language_code,
                                log_callback=self.log
                            )
                            if srt_path:
                                self.log(f"   ✅ Subtitle file created: {srt_path}")
                            else:
                                self.log(f"   ⚠️ Subtitle generation returned None - No speech detected or error occurred")
                                self.log(f"   💡 Tip: Check if the video has clear audio")
                            if os.path.exists(audio_temp): 
                                os.remove(audio_temp)
                        else:
                            self.log(f"   ⚠️ Audio extraction failed")
                except Exception as e:
                    self.log(f"   ❌ Subtitle Error ({filename}): {e}")
                    import traceback
                    self.log(f"   Traceback: {traceback.format_exc()}")


            # 2. Process Video
            # Create progress callback for real-time updates
            def update_ffmpeg_progress(percent):
                # Calculate base progress from completed files
                base_percent = (completed / total) * 100
                # Add current file's contribution (percent of this file * weight of one file)
                file_contribution = (percent / 100) * (100 / total)
                overall_percent = base_percent + file_contribution
                self.update_progress_percent(int(overall_percent), filename)
            
            is_success = process_video_with_ffmpeg(
                input_path, output_path, settings, 
                srt_file=srt_path, 
                log_callback=self.log,
                progress_callback=update_ffmpeg_progress,
                check_stop_signal=lambda: not self.is_processing
            )
            
            
            # Clean up temporary SRT file after processing
            if srt_path and os.path.exists(srt_path):
                try:
                    os.remove(srt_path)
                    self.log(f"   🗑️ Cleaned up temp subtitle file")
                except Exception as e:
                    self.log(f"   ⚠️ Could not delete temp SRT: {e}")
            
            # Add Text Outro if enabled (NEW)
            if is_success and settings.get('enable_outro_text'):
                try:
                    from utils.text_outro_helper import add_text_outro_to_video
                    import tempfile
                    
                    self.log(f"   📝 Adding text outro to: {filename}")
                    
                    # Create temp output path
                    temp_outro_output = os.path.join(
                        tempfile.gettempdir(),
                        f"with_outro_{filename}"
                    )
                    
                    # Add text outro
                    outro_success = add_text_outro_to_video(
                        output_path,
                        temp_outro_output,
                        settings,
                        log_callback=self.log
                    )
                    
                    # Replace original if successful
                    if outro_success and os.path.exists(temp_outro_output):
                        try:
                            # Replace original with outro version
                            os.replace(temp_outro_output, output_path)
                            self.log(f"   ✅ Text outro added successfully!")
                        except Exception as e:
                            self.log(f"   ⚠️ Failed to replace with outro version: {e}")
                            # Cleanup temp file
                            try:
                                os.remove(temp_outro_output)
                            except:
                                pass
                    else:
                        self.log(f"   ⚠️ Text outro creation failed, using video without outro")
                        
                except Exception as e:
                    self.log(f"   ⚠️ Text outro error: {e}")
                    # Continue without outro - don't fail the whole process
            
            with lock:
                completed += 1
                if is_success:
                    success_count += 1
                    self.log(f"✅ [{completed}/{total}] Xong: {filename}")
                    
                    # Notify per video completion
                    notify_video_complete(self, filename, completed, total)
                else:
                    fail_count += 1
                
                # Update progress: Completed
                self.update_progress(completed, total, filename)
        
        # Execute in ThreadPool
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(_process_single_file, f) for f in files]
                
                # Use as_completed to catch exceptions from workers
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as exc:
                        self.log(f"🔥 WORKER CRASH: {exc}")
                        import traceback
                        traceback.print_exc()
            
            self.log(f"🎉 Hoàn tất! Thành công: {success_count}, Thất bại: {fail_count}")
            
            # Notify completion
            notify_all_complete(self, success_count)
            
            # Restore window from tray
            self.root.after(100, self.restore_from_tray)
            
            # Show messagebox after restore
            self.root.after(500, lambda: messagebox.showinfo("Done", f"Đã xử lý xong {total} video!\n✅ Thành công: {success_count}\n❌ Thất bại: {fail_count}"))
            
        except Exception as e:
            self.log(f"CRITICAL ERROR: {e}")
        
        self.is_processing = False
        self.status_var.set("Ready")
        
        # Reset buttons
        self.stop_btn.configure(state="disabled")
        self.export_btn.configure(state="normal")

    def on_media_select(self, event):
        """Handle video selection for preview"""
        selection = self.tree_media.selection()
        if not selection:
            return
        
        filename = self.tree_media.item(selection[0])['values'][0]
        filepath = os.path.join(self.input_dir.get(), filename)
        
        # Stop previous preview
        self.stop_preview = True
        
        # Generate new ID for this viewing session
        self.preview_id += 1
        current_id = self.preview_id
        
        # Clear old image to prevent flicker
        try:
            self.preview_label.configure(image='', text='Đang tải...')
            self.preview_label.pack(expand=True) # REMOVED fill='both' to prevent forced resizing loop
            self.preview_label.imgtk = None
        except:
            pass
        
        # Small delay to ensure old thread stops (Increased for stability)
        import time
        time.sleep(0.15)
        
        # Start new preview
        self.stop_preview = False
        self.preview_thread = threading.Thread(target=self.play_preview_thread, args=(filepath, current_id), daemon=True)
        self.preview_thread.start()

    def start_preview_polling(self):
        """Main Thread Loop: Polls for new frames and updates UI safely"""
        # Stop any existing polling
        if hasattr(self, '_poll_id') and self._poll_id:
            try:
                self.root.after_cancel(self._poll_id)
            except: pass
            
        def _poll():
            if self.stop_preview:
                return
                
            try:
                # Check if new frame is available from worker
                if hasattr(self, 'latest_frame') and self.latest_frame is not None:
                    # Create Image in MAIN THREAD (Crucial for stability)
                    frame_arr = self.latest_frame
                    # Store current preview dimensions for drag handlers
                    self.preview_img_h, self.preview_img_w = frame_arr.shape[:2]
                    img = Image.fromarray(frame_arr)
                    
                    # --- DYNAMIC SCALING (To fit window) ---
                    try:
                        w_cont = self.preview_label.winfo_width()
                        h_cont = self.preview_label.winfo_height()
                        
                        # Only scale if container is valid and significantly different size
                        if w_cont > 50 and h_cont > 50:
                            # Calculate aspect ratios
                            img_ratio = img.width / img.height
                            cont_ratio = w_cont / h_cont
                            
                            # Standard "Contain" logic to maximize size
                            if img_ratio > cont_ratio:
                                # Width constrained
                                new_w = w_cont
                                new_h = int(w_cont / img_ratio)
                            else:
                                # Height constrained
                                new_h = h_cont
                                new_w = int(h_cont * img_ratio)
                                
                            # Resize properly using high-quality resampling
                            img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
                            
                            # Debug/Store display dims for mouse events mapping
                            self.preview_display_w = new_w
                            self.preview_display_h = new_h
                    except:
                        pass
                    # ---------------------------------------

                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    # Check if widget still exists before updating
                    try:
                        if self.preview_label.winfo_exists():
                            # Store old image reference
                            old_img = getattr(self.preview_label, 'imgtk', None)
                            
                            # Update with new image
                            self.preview_label.imgtk = imgtk # Keep ref
                            self.preview_label.configure(image=imgtk, text="")
                            
                            # Delete old image to free memory
                            if old_img:
                                try:
                                    del old_img
                                except:
                                    pass
                    except tk.TclError:
                        # Widget was destroyed, stop polling
                        return
                        
                    # Explicitly delete PIL image object
                    del img
            except Exception as e:
                # Silently handle errors (don't spam console)
                pass
                
            # ADAPTIVE POLLING RATE (Performance Optimization)
            # Adjust frame rate based on window size and activity
            try:
                window_width = self.root.winfo_width()
                window_height = self.root.winfo_height()
                
                # Small window (< 800px wide) = Lower frame rate to reduce CPU load
                if window_width < 800:
                    base_interval = 50  # 20 FPS for small windows
                elif window_width < 1200:
                    base_interval = 40  # 25 FPS for medium windows
                else:
                    base_interval = 33  # 30 FPS for large windows
                
                # Boost to 60 FPS when dragging sticker for smooth movement
                poll_interval = 16 if self.sticker_dragging else base_interval
            except:
                # Fallback
                poll_interval = 16 if self.sticker_dragging else 40
            
            self._poll_id = self.root.after(poll_interval, _poll)
            
        _poll()

    def play_preview_thread(self, filepath, thread_id):
        """Worker Thread: Reads frames, Resizes to Preview Quality (480p). NO UI interaction."""
        try:
            import time
            import numpy as np
            import gc
            
            # Start UI Polling from Main Thread context
            self.root.after(0, self.start_preview_polling)

            cap = cv2.VideoCapture(filepath)
            # Get video info for player controls (NEW)
            self.video_total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
            # Target 24 FPS (Cinematic/Smooth) - Safe limit
            target_fps = 24.0
            frame_interval = 1.0 / target_fps
            
            frame_count = 0
            
            while not self.stop_preview and cap.isOpened():
                start_time = time.time()
                
                if self.preview_id != thread_id:
                    break
                # Handle Pause (NEW)
                while self.is_paused and not self.stop_preview:
                    time.sleep(0.1)
                    if self.preview_id != thread_id:
                        break

                # Handle Seek (NEW)
                if self.seeking:
                    try:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_target_frame)
                        frame_count = self.seek_target_frame
                        self.seeking = False
                    except:
                        self.seeking = False
                # Update seek bar and time display (NEW)
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                self.video_current_frame = current_frame
                if self.video_total_frames > 0:
                    seek_percent = (current_frame / self.video_total_frames) * 100
                    self.root.after(0, lambda p=seek_percent: self.seek_var.set(p))
                
                current_time = current_frame / self.video_fps if self.video_fps > 0 else 0
                total_time = self.video_total_frames / self.video_fps if self.video_fps > 0 else 0
                time_text = f"{self.format_time(current_time)} / {self.format_time(total_time)}"
                self.root.after(0, lambda t=time_text: self.time_label.configure(text=t))
                # Loop video
                try:
                    if cap.get(cv2.CAP_PROP_POS_FRAMES) >= cap.get(cv2.CAP_PROP_FRAME_COUNT):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

                    ret, frame = cap.read()
                    if not ret:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        time.sleep(0.1)
                        continue
                except:
                    break
                
                frame_count += 1
                
                # Apply Speed Preview (NEW)
                # Simulate speed by skipping frames for faster playback
                # or slowing down frame interval for slower playback
                speed_factor = self.speed_factor.get() if self.enable_speed.get() else 1.0
                
                # For speed > 1.0 (faster), skip frames
                if speed_factor > 1.0:
                    # Skip frames to simulate speed
                    # E.g., 2x speed = skip every other frame
                    skip_frames = int(speed_factor) - 1
                    if skip_frames > 0 and frame_count % (skip_frames + 1) != 0:
                        continue  # Skip this frame
                
                # Adjust playback interval for speed
                adjusted_interval = frame_interval / speed_factor
                if frame_count % 50 == 0:
                    gc.collect() # Force GC every 50 frames to prevent RAM spike
                
                # --- PROCESSING (Background) ---
                
                # --- PROCESSING (Background) ---
                
                # 1. Base Resize (Standard Preview Size 720p - Increased for better visibility)
                # Keep this as the "Container" size basis
                h_base, w_base = frame.shape[:2]
                proc_h = 720  # UPDATED: Increased from 480 to 720
                
                if h_base > proc_h:
                    scale = proc_h / h_base
                    proc_w = int(w_base * scale)
                    if proc_w > 1280:
                         scale = 1280 / w_base
                         proc_w = 1280
                         proc_h = int(h_base * scale)
                    
                    # This frame serves as the SOURCE for both BG and FG
                    frame_base = cv2.resize(frame, (proc_w, proc_h), interpolation=cv2.INTER_LINEAR)
                else:
                    frame_base = frame.copy()
                    proc_w, proc_h = w_base, h_base

                # 2. Determine Canvas Size (Background)
                ratio_str = self.aspect_ratio.get()
                
                target_ratio = None
                if "9:16" in ratio_str: target_ratio = 9/16
                elif "16:9" in ratio_str: target_ratio = 16/9
                elif "1:1" in ratio_str: target_ratio = 1.0
                elif "4:3" in ratio_str: target_ratio = 4/3
                
                # If Original or simple mode, use current video ratio as canvas ratio
                if target_ratio is None:
                    target_ratio = proc_w / proc_h

                # Calculate Canvas dimensions
                if target_ratio < 1.0: # Portrait
                    c_h = proc_h
                    c_w = int(proc_h * target_ratio)
                else: # Landscape or Square
                    c_w = proc_w
                    c_h = int(proc_w / target_ratio)
                
                # 3. Create Background (Canvas)
                if self.enable_blur.get() and self.blur_amount.get() > 0:
                     # Stretch base frame to fill canvas then Blur
                     bg_stretched = cv2.resize(frame_base, (c_w, c_h), interpolation=cv2.INTER_LINEAR)
                     
                     blur_val = self.blur_amount.get()
                     k = int(blur_val * 6) * 2 + 1
                     if k > 1:
                         try:
                             canvas = cv2.GaussianBlur(bg_stretched, (k, k), 0)
                         except: canvas = bg_stretched
                     else:
                         canvas = bg_stretched
                else:
                     canvas = np.zeros((c_h, c_w, 3), dtype=np.uint8)

                # 4. Prepare Foreground (Scaled Video)
                # 4. Prepare Foreground (Scaled Video)
                resize_mode = self.resize_mode.get()
                
                if "Fill" in resize_mode or "Lấp đầy" in resize_mode:
                    # Fill logic: Cover the canvas (crop excess)
                    scale_preview = max(c_w / w_base, c_h / h_base)
                else:
                    # Fit logic: Ensure video fits inside canvas
                    scale_preview = min(c_w / w_base, c_h / h_base)
                
                # Base Dimensions
                w_fitted = w_base * scale_preview
                h_fitted = h_base * scale_preview
                
                # Apply User Scale (Percent)
                s_w = self.scale_w.get()
                s_h = self.scale_h.get()
                
                new_scaled_w = max(1, int(w_fitted * s_w))
                new_scaled_h = max(1, int(h_fitted * s_h))
                
                frame_fg = cv2.resize(frame_base, (new_scaled_w, new_scaled_h), interpolation=cv2.INTER_LINEAR)
                
                # Apply Color Filter (NEW - Preview)
                color_filter = self.color_filter.get()
                if color_filter and "None" not in color_filter and "Gốc" not in color_filter:
                    if "Đen Trắng" in color_filter or "B&W" in color_filter:
                        # Black & White
                        frame_fg = cv2.cvtColor(frame_fg, cv2.COLOR_BGR2GRAY)
                        frame_fg = cv2.cvtColor(frame_fg, cv2.COLOR_GRAY2BGR)
                    elif "Sepia" in color_filter or "Cổ điển" in color_filter:
                        # Sepia tone
                        kernel = np.array([[0.272, 0.534, 0.131],
                                          [0.349, 0.686, 0.168],
                                          [0.393, 0.769, 0.189]])
                        frame_fg = cv2.transform(frame_fg, kernel)
                        frame_fg = np.clip(frame_fg, 0, 255).astype(np.uint8)
                    elif "Vintage" in color_filter or "Phim cũ" in color_filter:
                        # Vintage (reduce saturation, slight yellow tint)
                        hsv = cv2.cvtColor(frame_fg, cv2.COLOR_BGR2HSV).astype(np.float32)
                        hsv[:, :, 1] = hsv[:, :, 1] * 0.8  # Reduce saturation
                        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
                        frame_fg = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                        # Add slight yellow tint
                        frame_fg[:, :, 0] = np.clip(frame_fg[:, :, 0] * 0.9, 0, 255)  # Reduce blue
                        frame_fg[:, :, 1] = np.clip(frame_fg[:, :, 1] * 1.0, 0, 255)  # Keep green
                        frame_fg[:, :, 2] = np.clip(frame_fg[:, :, 2] * 1.1, 0, 255)  # Boost red
                    elif "Cold" in color_filter or "Lạnh" in color_filter:
                        # Cold (boost blue, reduce red)
                        frame_fg[:, :, 0] = np.clip(frame_fg[:, :, 0] * 1.3, 0, 255)  # Boost blue
                        frame_fg[:, :, 2] = np.clip(frame_fg[:, :, 2] * 0.8, 0, 255)  # Reduce red
                    elif "Warm" in color_filter or "Ấm" in color_filter:
                        # Warm (boost red/yellow, reduce blue)
                        frame_fg[:, :, 0] = np.clip(frame_fg[:, :, 0] * 0.7, 0, 255)  # Reduce blue
                        frame_fg[:, :, 2] = np.clip(frame_fg[:, :, 2] * 1.3, 0, 255)  # Boost red
                
                # Apply Brightness (NEW - Preview)
                if self.enable_brightness.get():
                    brightness = self.brightness.get()
                    if brightness != 1.0:
                        # Brightness adjustment: multiply all channels
                        # brightness > 1.0 = brighter, < 1.0 = darker
                        frame_fg = frame_fg.astype(np.float32)
                        frame_fg = frame_fg * brightness
                        frame_fg = np.clip(frame_fg, 0, 255).astype(np.uint8)
                
                # Mirror FG only
                if self.mirror_enabled.get():
                    frame_fg = cv2.flip(frame_fg, 1)

                # 5. Paste FG onto BG (Center)
                y_off = (c_h - new_scaled_h) // 2
                x_off = (c_w - new_scaled_w) // 2

                # Safe Paste Logic (Handle out of bounds due to Zoom)
                y1, y2 = max(0, y_off), min(c_h, y_off + new_scaled_h)
                x1, x2 = max(0, x_off), min(c_w, x_off + new_scaled_w)
                
                # Source coords
                sy1, sy2 = max(0, -y_off), max(0, -y_off) + (y2 - y1)
                sx1, sx2 = max(0, -x_off), max(0, -x_off) + (x2 - x1)

                if (y2 > y1) and (x2 > x1):
                    canvas[y1:y2, x1:x2] = frame_fg[sy1:sy2, sx1:sx2]
                
                # 6. Draw Subtitle Black Bar (NEW - Preview)
                if self.enable_subtitle_bar.get():
                    bar_height_px = self.subtitle_bar_height.get()
                    # Scale bar height to preview resolution
                    # Original video might be 1280px tall, preview is ~480px
                    # So we scale proportionally
                    bar_height_preview = int(bar_height_px * (c_h / 1280.0))  # Assuming 720p/1080p base
                    
                    # Ensure bar doesn't exceed canvas height
                    bar_height_preview = min(bar_height_preview, c_h // 3)  # Max 1/3 of height
                    
                    if bar_height_preview > 0:
                        # Draw black rectangle at bottom
                        # cv2.rectangle(img, pt1, pt2, color, thickness=-1 for filled)
                        cv2.rectangle(canvas, 
                                    (0, c_h - bar_height_preview),  # Top-left of bar
                                    (c_w, c_h),                      # Bottom-right (full width, bottom edge)
                                    (0, 0, 0),                       # Black color
                                    -1)                              # Filled
                
                # 7. Overlay Sticker (NEW - Preview)
                if self.enable_sticker.get():
                    sticker_path = self.sticker_path.get()
                    if sticker_path and os.path.exists(sticker_path):
                        try:
                            from PIL import Image as PILImage
                            
                            # Load sticker
                            sticker_pil = PILImage.open(sticker_path)
                            
                            # Convert to RGBA if not already
                            if sticker_pil.mode != 'RGBA':
                                sticker_pil = sticker_pil.convert('RGBA')
                            
                            # Calculate sticker size based on scale setting
                            sticker_scale = self.sticker_scale.get()
                            sticker_w = int(c_w * sticker_scale)
                            sticker_h = int(sticker_w * (sticker_pil.height / sticker_pil.width))
                            
                            # Resize sticker
                            sticker_pil = sticker_pil.resize((sticker_w, sticker_h), PILImage.Resampling.LANCZOS)
                            
                            # Convert to numpy array
                            sticker_np = np.array(sticker_pil)
                            
                            # Calculate position
                            sticker_pos = self.sticker_pos.get()
                            margin = 20
                            
                            # Check if using custom drag position
                            if "Tùy chỉnh" in sticker_pos or "Custom" in sticker_pos:
                                # Use drag position (normalized 0-1)
                                x_pos = int(self.sticker_drag_x.get() * c_w)
                                y_pos = int(self.sticker_drag_y.get() * c_h)
                            else:
                                # Use preset positions (Robust Logic)
                                # Default: Bottom-Right
                                x_pos = c_w - sticker_w - margin
                                y_pos = c_h - sticker_h - margin
                                
                                # Vertical Logic
                                if "Top" in sticker_pos or "trên" in sticker_pos:
                                    y_pos = margin
                                elif "Bottom" in sticker_pos or "dưới" in sticker_pos:
                                    y_pos = c_h - sticker_h - margin
                                elif "Center" in sticker_pos or "giữa" in sticker_pos:
                                    y_pos = (c_h - sticker_h) // 2
                                    
                                # Horizontal Logic
                                if "Left" in sticker_pos or "trái" in sticker_pos:
                                    x_pos = margin
                                elif "Right" in sticker_pos or "phải" in sticker_pos:
                                    x_pos = c_w - sticker_w - margin
                                elif "Center" in sticker_pos or "giữa" in sticker_pos:
                                    x_pos = (c_w - sticker_w) // 2
                            
                            # Ensure sticker is within bounds
                            x_pos = max(0, min(x_pos, c_w - sticker_w))
                            y_pos = max(0, min(y_pos, c_h - sticker_h))
                            
                            # Overlay with alpha blending
                            if sticker_np.shape[2] == 4:  # Has alpha channel
                                # Extract RGB and Alpha
                                sticker_rgb = sticker_np[:, :, :3]
                                alpha_mask = sticker_np[:, :, 3] / 255.0
                                
                                # Define ROI on canvas
                                y1, y2 = y_pos, y_pos + sticker_h
                                x1, x2 = x_pos, x_pos + sticker_w
                                
                                # Clip to canvas bounds
                                y1 = max(0, y1); y2 = min(c_h, y2);
                                x1 = max(0, x1); x2 = min(c_w, x2);
                                
                                # Adjustment for source if clipped
                                sy1 = max(0, -y_pos); sy2 = sy1 + (y2 - y1);
                                sx1 = max(0, -x_pos); sx2 = sx1 + (x2 - x1);
                                
                                if y2 > y1 and x2 > x1:
                                    # Blend
                                    for c in range(3):
                                        canvas[y1:y2, x1:x2, c] = (alpha_mask[sy1:sy2, sx1:sx2] * sticker_rgb[sy1:sy2, sx1:sx2, c] + 
                                                                 (1 - alpha_mask[sy1:sy2, sx1:sx2]) * canvas[y1:y2, x1:x2, c])
                                                                 
                                    # Draw Selection Border (CapCut Style)
                                    # Always draw it to show it's interactable, or at least when Custom mode/Hover
                                    # For now, always draw a thin dashed-like or solid white box to indicate "You can move me"
                                    # White border with black outline for visibility
                                    cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 0), 3) # Outer Black
                                    cv2.rectangle(canvas, (x1, y1), (x2, y2), (255, 255, 255), 1) # Inner White
                            else:
                                # No alpha, just paste directly
                                y1, y2 = y_pos, y_pos + sticker_h
                                x1, x2 = x_pos, x_pos + sticker_w
                                # Clip to canvas bounds
                                y1 = max(0, y1); y2 = min(c_h, y2);
                                x1 = max(0, x1); x2 = min(c_w, x2);
                                
                                # Adjustment for source if clipped
                                sy1 = max(0, -y_pos); sy2 = sy1 + (y2 - y1);
                                sx1 = max(0, -x_pos); sx2 = sx1 + (x2 - x1);

                                if y2 > y1 and x2 > x1:
                                    canvas[y1:y2, x1:x2] = sticker_np[sy1:sy2, sx1:sx2, :3]
                                    # Draw Selection Border (CapCut Style)
                                    cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 0), 3) # Outer Black
                                    cv2.rectangle(canvas, (x1, y1), (x2, y2), (255, 255, 255), 1) # Inner White
                        
                        except Exception as e:
                            # Silently fail if sticker can't be loaded
                            pass
                
                final_frame_ready = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)

                # SHARE WITH MAIN THREAD
                self.latest_frame = final_frame_ready
                
                # Sleep with adjusted interval for speed
                elapsed = time.time() - start_time
                wait = adjusted_interval - elapsed
                if wait < 0.01: wait = 0.01
                time.sleep(wait)
            
        except Exception as e:
            print(f"Preview error: {e}")
        finally:
            # CRITICAL: Always release video capture to prevent file locks
            try:
                if 'cap' in locals() and cap is not None:
                    cap.release()
            except:
                pass
            self.latest_frame = None

