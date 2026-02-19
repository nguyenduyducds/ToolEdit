
import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox

# App Constants
APP_VERSION = "2.0.2"
DEFAULT_INPUT_DIR = "input"
DEFAULT_OUTPUT_DIR = "output"

# Default Settings
DEFAULT_START_TIME = 0
DEFAULT_BLUR_AMOUNT = 0  # Changed from 15 to 0
DEFAULT_BRIGHTNESS = 1.0
DEFAULT_ZOOM_FACTOR = 1.0
DEFAULT_SPEED_FACTOR = 1.0
DEFAULT_MIRROR_ENABLED = False

class ConfigManager:
    """
    Manages loading, saving, and resetting application configuration.
    """
    def __init__(self, gui):
        """
        Initialize with reference to main GUI instance to access variables.
        """
        self.gui = gui
        # Hidden auto-config file
        self.auto_config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".video_editor_config.json")
        
    def init_settings_vars(self):
        """Initialize Tkinter variables for settings"""
        g = self.gui
        
        # Video Settings
        g.start_time = tk.IntVar(value=DEFAULT_START_TIME)
        g.duration = tk.IntVar(value=0) # 0 = All
        g.blur_amount = tk.IntVar(value=DEFAULT_BLUR_AMOUNT)
        g.brightness = tk.DoubleVar(value=DEFAULT_BRIGHTNESS)
        g.zoom_factor = tk.DoubleVar(value=DEFAULT_ZOOM_FACTOR)
        g.speed_factor = tk.DoubleVar(value=DEFAULT_SPEED_FACTOR)
        g.mirror_enabled = tk.BooleanVar(value=DEFAULT_MIRROR_ENABLED)
        g.convert_to_portrait = tk.BooleanVar(value=False)
        g.aspect_ratio = tk.StringVar(value="9:16 (TikTok/Shorts)")
        g.resize_mode = tk.StringVar(value="Thêm viền (Fit)")
        g.uniform_scale = tk.BooleanVar(value=True) # Default uniform scaling
        g.scale_w = tk.DoubleVar(value=1.0)
        g.scale_h = tk.DoubleVar(value=1.0)
        g.color_filter = tk.StringVar(value="Gốc (None)")
        
        # Toggles
        g.enable_zoom = tk.BooleanVar(value=False)
        g.enable_speed = tk.BooleanVar(value=False)
        g.enable_blur = tk.BooleanVar(value=False)  # Changed from True to False
        g.enable_brightness = tk.BooleanVar(value=False)
        g.simple_mode = tk.BooleanVar(value=False) # Fast preview/simple mode
        
        # Audio
        g.volume_boost = tk.DoubleVar(value=1.0)
        g.bass_boost = tk.IntVar(value=0)
        g.treble_boost = tk.IntVar(value=0)
        
        # Subtitles (Whisper)
        g.enable_subtitles = tk.BooleanVar(value=False)
        g.subtitle_language = tk.StringVar(value="auto (Tự động)")  # Auto-detect by default
        g.force_google_subs = tk.BooleanVar(value=False)
        g.subtitle_font_size = tk.IntVar(value=14)
        g.enable_subtitle_bar = tk.BooleanVar(value=False)
        g.subtitle_bar_height = tk.IntVar(value=80)
        
        # Intro/Outro
        g.enable_intro = tk.BooleanVar(value=False)
        g.intro_path = tk.StringVar(value="")
        g.enable_outro = tk.BooleanVar(value=False)
        g.outro_path = tk.StringVar(value="")
        
        # Outro Text
        g.enable_outro_text = tk.BooleanVar(value=False)
        g.outro_text_duration = tk.IntVar(value=5)
        g.outro_text_content = tk.StringVar(value="")
        g.outro_text_font_size = tk.IntVar(value=60)
        g.outro_text_font_color = tk.StringVar(value="white")
        g.outro_text_bg_color = tk.StringVar(value="black")
        g.outro_text_position = tk.StringVar(value="center")
        g.outro_text_animation = tk.StringVar(value="fade")
        g.outro_text_animation = tk.StringVar(value="fade")
        g.outro_text_style = tk.StringVar(value="Đè lên video (Overlay)")
        g.outro_text_box = tk.BooleanVar(value=False)
        g.outro_text_box_padding = tk.IntVar(value=20)  # NEW: Padding for box
        g.outro_text_font = tk.StringVar(value="Arial (Mặc định)") # NEW: Font variable

        
        # Stickers
        g.stickers_list = [] # List of dicts (path, pos, scale, x, y)
        g.enable_sticker = tk.BooleanVar(value=False) # Master toggle
        g.sticker_path = tk.StringVar(value="") # Backup for single sticker legacy
        g.sticker_pos = tk.StringVar(value="Góc phải dưới")
        g.sticker_scale = tk.DoubleVar(value=0.2)
        g.sticker_drag_x = tk.DoubleVar(value=0.8)
        g.sticker_drag_y = tk.DoubleVar(value=0.8)
        
        # System
        g.output_dir = tk.StringVar(value=os.path.abspath(DEFAULT_OUTPUT_DIR))
        g.num_threads = tk.IntVar(value=4) # Will be updated by detect_optimal_threads
        g.use_gpu = tk.BooleanVar(value=True)
        g.status_var = tk.StringVar(value="Sẵn sàng")
        g.enable_minimize_to_tray = tk.BooleanVar(value=False)

    def auto_save_config(self):
        """Auto-save current settings to hidden config file (no user interaction)"""
        g = self.gui
        try:
            # Collect all settings
            config = {
                "version": APP_VERSION,
                "theme": g.current_theme,
                "output_dir": g.output_dir.get(),
                "video": {
                    "start_time": g.start_time.get(),
                    "duration": g.duration.get(),
                    "blur_amount": g.blur_amount.get(),
                    "brightness": g.brightness.get(),
                    "zoom_factor": g.zoom_factor.get(),
                    "speed_factor": g.speed_factor.get(),
                    "mirror_enabled": g.mirror_enabled.get(),
                    "aspect_ratio": g.aspect_ratio.get(),
                    "resize_mode": g.resize_mode.get(),
                    "uniform_scale": g.uniform_scale.get(),
                    "scale_w": g.scale_w.get(),
                    "scale_h": g.scale_h.get(),
                    "enable_zoom": g.enable_zoom.get(),
                    "enable_speed": g.enable_speed.get(),
                    "enable_blur": g.enable_blur.get(),
                    "enable_brightness": g.enable_brightness.get(),
                    "color_filter": g.color_filter.get()
                },
                "audio": {
                    "volume_boost": g.volume_boost.get(),
                    "bass_boost": g.bass_boost.get(),
                    "treble_boost": g.treble_boost.get()
                },
                "subtitle": {
                    "enable_subtitles": g.enable_subtitles.get(),
                    "subtitle_language": g.subtitle_language.get(),
                    "force_google_subs": g.force_google_subs.get(),
                    "enable_subtitle_bar": g.enable_subtitle_bar.get(),
                    "subtitle_bar_height": g.subtitle_bar_height.get()
                },
                "intro_outro": {
                    "enable_intro": g.enable_intro.get(),
                    "intro_path": g.intro_path.get(),
                    "enable_outro": g.enable_outro.get(),
                    "outro_path": g.outro_path.get(),
                    # Text Outro
                    "enable_outro_text": getattr(g, 'enable_outro_text', tk.BooleanVar(value=0)).get(),
                    "outro_text_duration": getattr(g, 'outro_text_duration', tk.IntVar(value=5)).get(),
                    "outro_text_content": getattr(g, 'outro_text_content', tk.StringVar(value="")).get(),
                    "outro_text_box": getattr(g, 'outro_text_box', tk.BooleanVar(value=False)).get(),
                    "outro_text_box_padding": getattr(g, 'outro_text_box_padding', tk.IntVar(value=15)).get(),
                    "outro_text_style": getattr(g, 'outro_text_style', tk.StringVar(value="Overlay")).get(),
                    "outro_text_font": getattr(g, 'outro_text_font', tk.StringVar(value="Arial (Mặc định)")).get()
                },
                "stickers": {
                    "stickers_list": g.stickers_list,
                    "sticker_pos": g.sticker_pos.get(),
                    "sticker_scale": g.sticker_scale.get()
                },
                "system": {
                    "num_threads": g.num_threads.get(),
                    "use_gpu": g.use_gpu.get(),
                    "enable_minimize_to_tray": g.enable_minimize_to_tray.get()
                }
            }
            
            # Save to hidden file
            with open(self.auto_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Auto-saved config to: {self.auto_config_file}")
            
        except Exception as e:
            print(f"⚠️ Auto-save config failed: {e}")

    def auto_load_config(self):
        """Auto-load settings from hidden config file (no user interaction)"""
        g = self.gui
        from utils.app_utils import detect_optimal_threads
        
        try:
            if not os.path.exists(self.auto_config_file):
                print("ℹ️ No saved config found, using defaults")
                return
            
            with open(self.auto_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Application Logic
            if "theme" in config:
                saved_theme = config["theme"]
                if saved_theme != g.current_theme:
                    g.current_theme = saved_theme
                    # Theme button update handled by toggle_theme caller usually
                    # But here we just set variable, actual theme apply happens later in main
            
            if "output_dir" in config:
                out_dir = config["output_dir"]
                if out_dir and os.path.exists(out_dir):
                    g.output_dir.set(out_dir)

            # Apply Video Settings
            if "video" in config:
                v = config["video"]
                g.start_time.set(v.get("start_time", DEFAULT_START_TIME))
                g.duration.set(v.get("duration", 0))
                g.blur_amount.set(v.get("blur_amount", DEFAULT_BLUR_AMOUNT))
                g.brightness.set(v.get("brightness", DEFAULT_BRIGHTNESS))
                g.zoom_factor.set(v.get("zoom_factor", DEFAULT_ZOOM_FACTOR))
                g.speed_factor.set(v.get("speed_factor", DEFAULT_SPEED_FACTOR))
                g.mirror_enabled.set(v.get("mirror_enabled", DEFAULT_MIRROR_ENABLED))
                g.aspect_ratio.set(v.get("aspect_ratio", "Giữ nguyên (Original)"))
                g.resize_mode.set(v.get("resize_mode", "Thêm viền (Fit)"))
                g.uniform_scale.set(v.get("uniform_scale", False))
                g.scale_w.set(v.get("scale_w", 1.0))
                g.scale_h.set(v.get("scale_h", 1.0))
                g.enable_zoom.set(v.get("enable_zoom", False))
                g.enable_speed.set(v.get("enable_speed", False))
                g.enable_blur.set(v.get("enable_blur", False))
                g.enable_brightness.set(v.get("enable_brightness", False))
                g.color_filter.set(v.get("color_filter", "Gốc (None)"))
            
            if "audio" in config:
                a = config["audio"]
                g.volume_boost.set(a.get("volume_boost", 1.0))
                g.bass_boost.set(a.get("bass_boost", 0))
                g.treble_boost.set(a.get("treble_boost", 0))
            
            if "subtitle" in config:
                s = config["subtitle"]
                g.enable_subtitles.set(s.get("enable_subtitles", False))
                g.subtitle_language.set(s.get("subtitle_language", "auto (Tự động)"))
                g.force_google_subs.set(s.get("force_google_subs", False))
                g.enable_subtitle_bar.set(s.get("enable_subtitle_bar", False))
                g.subtitle_bar_height.set(s.get("subtitle_bar_height", 80))
            
            if "intro_outro" in config:
                io = config["intro_outro"]
                g.enable_intro.set(io.get("enable_intro", False))
                g.intro_path.set(io.get("intro_path", ""))
                g.enable_outro.set(io.get("enable_outro", False))
                g.outro_path.set(io.get("outro_path", ""))
                
                # Labels update is handled by GUI refresh or explicit check
            
            if "stickers" in config:
                st = config["stickers"]
                g.stickers_list = st.get("stickers_list", [])
                g.sticker_pos.set(st.get("sticker_pos", "Góc phải dưới"))
                g.sticker_scale.set(st.get("sticker_scale", 0.2))
            
            if "system" in config:
                sys = config["system"]
                g.num_threads.set(sys.get("num_threads", detect_optimal_threads()))
                g.use_gpu.set(sys.get("use_gpu", True))
                g.enable_minimize_to_tray.set(sys.get("enable_minimize_to_tray", False))
            
            print(f"✅ Auto-loaded config from: {self.auto_config_file}")
            if hasattr(g, 'log'): g.log("✅ Đã tải cấu hình đã lưu")
            
        except Exception as e:
            print(f"⚠️ Auto-load config failed: {e}")

    def save_config(self):
        """Save config dialog"""
        g = self.gui
        filename = filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            title="Lưu cấu hình",
            filetypes=[("JSON Config", "*.json")],
            defaultextension=".json"
        )
        if filename:
            try:
                # Reuse auto_save logic but write to specific file
                # Copy-paste logic or make auto_save accept path?
                # Let's simple copy for safety
                config = {
                    "version": APP_VERSION,
                    "theme": g.current_theme,
                    "output_dir": g.output_dir.get(),
                    "video": {
                        "start_time": g.start_time.get(),
                        "duration": g.duration.get(),
                        "blur_amount": g.blur_amount.get(),
                        "brightness": g.brightness.get(),
                        "zoom_factor": g.zoom_factor.get(),
                        "speed_factor": g.speed_factor.get(),
                        "mirror_enabled": g.mirror_enabled.get(),
                        "aspect_ratio": g.aspect_ratio.get(),
                        "resize_mode": g.resize_mode.get(),
                        "uniform_scale": g.uniform_scale.get(),
                        "scale_w": g.scale_w.get(),
                        "scale_h": g.scale_h.get(),
                        "enable_zoom": g.enable_zoom.get(),
                        "enable_speed": g.enable_speed.get(),
                        "enable_blur": g.enable_blur.get(),
                        "enable_brightness": g.enable_brightness.get(),
                        "color_filter": g.color_filter.get()
                    },
                    "audio": {
                        "volume_boost": g.volume_boost.get(),
                        "bass_boost": g.bass_boost.get(),
                        "treble_boost": g.treble_boost.get()
                    },
                    "subtitle": {
                        "enable_subtitles": g.enable_subtitles.get(),
                        "subtitle_language": g.subtitle_language.get(),
                        "force_google_subs": g.force_google_subs.get(),
                        "enable_subtitle_bar": g.enable_subtitle_bar.get(),
                        "subtitle_bar_height": g.subtitle_bar_height.get()
                    },
                    "intro_outro": {
                        "enable_intro": g.enable_intro.get(),
                        "intro_path": g.intro_path.get(),
                        "enable_outro": g.enable_outro.get(),
                        "outro_path": g.outro_path.get(),
                        "enable_outro_text": getattr(g, 'enable_outro_text', tk.BooleanVar(value=0)).get(),
                        "outro_text_duration": getattr(g, 'outro_text_duration', tk.IntVar(value=5)).get(),
                        "outro_text_content": getattr(g, 'outro_text_content', tk.StringVar(value="")).get()
                    },
                    "stickers": {
                        "stickers_list": g.stickers_list,
                        "sticker_pos": g.sticker_pos.get(),
                        "sticker_scale": g.sticker_scale.get()
                    },
                    "system": {
                        "num_threads": g.num_threads.get(),
                        "use_gpu": g.use_gpu.get(),
                        "enable_minimize_to_tray": g.enable_minimize_to_tray.get()
                    }
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                g.log(f"✅ Đã lưu cấu hình ra: {filename}")
                messagebox.showinfo("Thành công", f"Đã lưu cấu hình:\n{os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu cấu hình:\n{e}")

    def load_config(self):
        """Load config dialog"""
        g = self.gui
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Tải cấu hình",
            filetypes=[("JSON Config", "*.json")]
        )
        if filename:
            try:
                # Temporary switch auto_config_file to this file, check logic, then switch back?
                # Faster to just copy paste load logic or extract common loader
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Same loading logic as auto_load...
                if "theme" in config:
                    saved_theme = config["theme"]
                    if saved_theme != g.current_theme:
                        g.current_theme = saved_theme
                        # Let Main Window handle UI update
                        if hasattr(g, 'toggle_theme_ui_only'): 
                             g.toggle_theme_ui_only() # Hypothetical method
                
                if "output_dir" in config:
                    out_dir = config["output_dir"]
                    if out_dir and os.path.exists(out_dir):
                        g.output_dir.set(out_dir)

                # Video
                if "video" in config:
                    v = config["video"]
                    g.start_time.set(v.get("start_time", DEFAULT_START_TIME))
                    g.duration.set(v.get("duration", 0))
                    g.blur_amount.set(v.get("blur_amount", DEFAULT_BLUR_AMOUNT))
                    g.brightness.set(v.get("brightness", DEFAULT_BRIGHTNESS))
                    g.zoom_factor.set(v.get("zoom_factor", DEFAULT_ZOOM_FACTOR))
                    g.speed_factor.set(v.get("speed_factor", DEFAULT_SPEED_FACTOR))
                    g.mirror_enabled.set(v.get("mirror_enabled", DEFAULT_MIRROR_ENABLED))
                    g.aspect_ratio.set(v.get("aspect_ratio", "Giữ nguyên (Original)"))
                    g.resize_mode.set(v.get("resize_mode", "Thêm viền (Fit)"))
                    g.uniform_scale.set(v.get("uniform_scale", False))
                    g.scale_w.set(v.get("scale_w", 1.0))
                    g.scale_h.set(v.get("scale_h", 1.0))
                    g.enable_zoom.set(v.get("enable_zoom", False))
                    g.enable_speed.set(v.get("enable_speed", False))
                    g.enable_blur.set(v.get("enable_blur", False))
                    g.enable_brightness.set(v.get("enable_brightness", False))
                    g.color_filter.set(v.get("color_filter", "Gốc (None)"))
                
                if "audio" in config:
                    a = config["audio"]
                    g.volume_boost.set(a.get("volume_boost", 1.0))
                    g.bass_boost.set(a.get("bass_boost", 0))
                    g.treble_boost.set(a.get("treble_boost", 0))

                if "subtitle" in config:
                    s = config["subtitle"]
                    g.enable_subtitles.set(s.get("enable_subtitles", False))
                    g.subtitle_language.set(s.get("subtitle_language", "auto (Tự động)"))
                    g.force_google_subs.set(s.get("force_google_subs", False))
                    g.enable_subtitle_bar.set(s.get("enable_subtitle_bar", False))
                    
                if "intro_outro" in config:
                    io = config["intro_outro"]
                    g.enable_intro.set(io.get("enable_intro", False))
                    g.intro_path.set(io.get("intro_path", ""))
                    g.enable_outro.set(io.get("enable_outro", False))
                    g.outro_path.set(io.get("outro_path", ""))
                    
                    if hasattr(g, 'enable_outro_text'): g.enable_outro_text.set(io.get("enable_outro_text", False))
                    if hasattr(g, 'outro_text_duration'): g.outro_text_duration.set(io.get("outro_text_duration", 5))
                    if hasattr(g, 'outro_text_content'): g.outro_text_content.set(io.get("outro_text_content", ""))
                    if hasattr(g, 'outro_text_box'): g.outro_text_box.set(io.get("outro_text_box", False))
                    if hasattr(g, 'outro_text_box_padding'): g.outro_text_box_padding.set(io.get("outro_text_box_padding", 15))
                    if hasattr(g, 'outro_text_style'): g.outro_text_style.set(io.get("outro_text_style", "Overlay"))
                    if hasattr(g, 'outro_text_font'): g.outro_text_font.set(io.get("outro_text_font", "Arial (Mặc định)"))
                    
                if "stickers" in config:
                    st = config["stickers"]
                    g.stickers_list = st.get("stickers_list", [])
                    g.sticker_pos.set(st.get("sticker_pos", "Góc phải dưới"))
                    g.sticker_scale.set(st.get("sticker_scale", 0.2))
                    if hasattr(g, 'refresh_video_stickers_list'): g.refresh_video_stickers_list()

                if "system" in config:
                    sys = config["system"]
                    from utils.app_utils import detect_optimal_threads
                    g.num_threads.set(sys.get("num_threads", detect_optimal_threads()))
                    g.use_gpu.set(sys.get("use_gpu", True))
                    g.enable_minimize_to_tray.set(sys.get("enable_minimize_to_tray", False))

                g.log(f"✅ Đã tải cấu hình từ: {filename}")
                messagebox.showinfo("Thành công", f"Đã tải cấu hình từ:\n{os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải cấu hình:\n{e}")

    def reset_config(self):
        """Reset ALL settings to defaults (0, 1.0, False, etc.)"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn Reset toàn bộ cài đặt về mặc định (0, 1.0)?"):
            g = self.gui
            
            # Video Settings - Reset to 0 or 1.0
            g.start_time.set(0)
            g.duration.set(0)
            g.blur_amount.set(0)  # 0 instead of 15
            g.brightness.set(1.0)
            g.zoom_factor.set(1.0)
            g.speed_factor.set(1.0)
            g.mirror_enabled.set(False)
            g.aspect_ratio.set("Giữ nguyên (Original)")
            g.resize_mode.set("Thêm viền (Fit)")
            g.uniform_scale.set(True)
            g.scale_w.set(1.0)
            g.scale_h.set(1.0)
            g.color_filter.set("Gốc (None)")
            
            # Toggles - All OFF
            g.enable_zoom.set(False)
            g.enable_speed.set(False)
            g.enable_blur.set(False)
            g.enable_brightness.set(False)
            
            # Audio - Reset to neutral
            g.volume_boost.set(1.0)
            g.bass_boost.set(0)
            g.treble_boost.set(0)
            
            # Subtitles - OFF
            g.enable_subtitles.set(False)
            g.subtitle_language.set("auto (Tự động)")
            g.force_google_subs.set(False)
            g.enable_subtitle_bar.set(False)
            g.subtitle_bar_height.set(80)
            
            # Intro/Outro - OFF
            g.enable_intro.set(False)
            g.intro_path.set("")
            g.enable_outro.set(False)
            g.outro_path.set("")
            if hasattr(g, 'enable_outro_text'): g.enable_outro_text.set(False)
            if hasattr(g, 'outro_text_duration'): g.outro_text_duration.set(5)
            if hasattr(g, 'outro_text_content'): g.outro_text_content.set("")
            if hasattr(g, 'outro_text_box'): g.outro_text_box.set(False)
            if hasattr(g, 'outro_text_box_padding'): g.outro_text_box_padding.set(15)
            if hasattr(g, 'outro_text_style'): g.outro_text_style.set("Overlay")
            if hasattr(g, 'outro_text_font'): g.outro_text_font.set("Arial (Mặc định)")
            
            # Stickers - Clear all
            g.stickers_list = []
            g.sticker_pos.set("Góc phải dưới")
            g.sticker_scale.set(0.2)
            if hasattr(g, 'refresh_video_stickers_list'): 
                g.refresh_video_stickers_list()
            
            # Log
            if hasattr(g, 'log'): 
                g.log("🔄 Đã reset TẤT CẢ cài đặt về mặc định (0, 1.0, OFF)")
            
            messagebox.showinfo("Thành công", "✅ Đã reset tất cả về mặc định!")

    def browse_output_dir(self):
        """Open dialog to select output directory"""
        path = filedialog.askdirectory(
            title="Chọn Thư Mục Xuất Video",
            initialdir=self.gui.output_dir.get()
        )
        if path:
            self.gui.output_dir.set(path)
            self.auto_save_config()  # Auto-save immediately
            if hasattr(self.gui, 'log'): self.gui.log(f"📂 Đã thay đổi thư mục xuất: {path}")
