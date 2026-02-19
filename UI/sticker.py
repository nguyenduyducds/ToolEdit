"""Sticker/Watermark Module - Handles overlay logic for video editing"""

import os
from PIL import Image
import cv2
import numpy as np
from pathlib import Path


class StickerLibrary:
    """Manages built-in sticker library (CapCut style)"""
    
    def __init__(self):
        self.stickers_dir = Path(__file__).parent.parent / "assets" / "stickers"
        self.config_file = self.stickers_dir / "stickers.json"
        
        self.categories = {
            "Emoji": ["❤️ Heart", "⭐ Star", "🔥 Fire", "👍 Thumbs Up", "⚡ Lightning"],
            "Watermark": ["📺 Subscribe", "▶️ Like & Subscribe", "🔔 Bell Icon"],
            "Custom": []  # User-added stickers (loaded from JSON)
        }
        
        # Ensure directory exists
        print(f"DEBUG: Stickes Dir: {self.stickers_dir.absolute()}")
        self.stickers_dir.mkdir(parents=True, exist_ok=True)
        
        # Load custom stickers from JSON file
        self._load_custom_stickers()
    
    def get_sticker_path(self, sticker_name):
        """Get full path to a sticker by name
        
        Args:
            sticker_name: Display name of sticker (e.g., "❤️ Heart" or "OPd6EH3Jiu00M.gif")
            
        Returns:
            Path to sticker file, or None if not found
        """
        # First, try exact filename match (for Giphy stickers with ID filenames)
        if '.' in sticker_name:  # Has extension
            path = self.stickers_dir / sticker_name
            if path.exists():
                return str(path)
        
        # Clean name (remove emoji prefix)
        clean_name = sticker_name.split()[-1].lower()
        
        # Search for file with various extensions
        possible_names = [
            f"{clean_name}.png",
            f"{clean_name}.gif",
            f"{clean_name}.jpg",
            f"{clean_name}.jpeg",
            f"{clean_name}_sticker.png",
            f"{clean_name}_sticker.gif",
            f"{clean_name}_watermark.png"
        ]
        
        for name in possible_names:
            path = self.stickers_dir / name
            if path.exists():
                return str(path)
        
        # Last resort: search directory for any file containing the clean name
        try:
            for file in self.stickers_dir.iterdir():
                if file.is_file() and clean_name in file.name.lower():
                    return str(file)
        except:
            pass
        
        return None
    
    def get_all_stickers(self):
        """Get all available stickers organized by category
        
        Returns:
            Dict of {category: [sticker_names]}
        """
        return self.categories.copy()
    
    def _load_custom_stickers(self):
        """Load custom stickers from JSON file AND auto-scan directory"""
        try:
            import json
            
            # First, scan directory for ALL image files
            all_stickers = []
            if self.stickers_dir.exists():
                for file in self.stickers_dir.iterdir():
                    if file.is_file() and file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                        # Skip built-in stickers (heart, star, etc.)
                        if file.stem not in ['heart', 'star', 'fire', 'lightning', 'thumbs', 'subscribe']:
                            all_stickers.append(file.name)
            
            # Load from JSON (for ordering/favorites)
            saved_order = []
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    saved_order = data.get("custom_stickers", [])
            
            # Combine: saved order first, then new files
            ordered_stickers = []
            for sticker in saved_order:
                if sticker in all_stickers:
                    ordered_stickers.append(sticker)
            
            # Add new stickers not in JSON
            for sticker in all_stickers:
                if sticker not in ordered_stickers:
                    ordered_stickers.append(sticker)
            
            self.categories["Custom"] = ordered_stickers
            
            # Update JSON with complete list
            if ordered_stickers != saved_order:
                self._save_custom_stickers()
            
            print(f"✅ Loaded {len(ordered_stickers)} custom stickers")
        except Exception as e:
            print(f"Error loading custom stickers: {e}")
            self.categories["Custom"] = []
    
    def _save_custom_stickers(self):
        """Save custom stickers to JSON file"""
        try:
            import json
            
            data = {
                "custom_stickers": self.categories["Custom"]
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved {len(self.categories['Custom'])} custom stickers")
        except Exception as e:
            print(f"Error saving custom stickers: {e}")
    
    def add_custom_sticker(self, file_path, display_name=None):
        """Add a custom sticker to library
        
        Args:
            file_path: Path to sticker image
            display_name: Optional display name (defaults to filename)
            
        Returns:
            True if successful
        """
        try:
            import shutil
            
            if not os.path.exists(file_path):
                return False
            
            # Copy to stickers directory (permanent storage)
            filename = os.path.basename(file_path)
            dest = self.stickers_dir / filename
            shutil.copy2(file_path, dest)
            
            # Add to custom category
            name = display_name or filename
            if name not in self.categories["Custom"]:
                self.categories["Custom"].append(name)
                # Save to JSON for persistence
                self._save_custom_stickers()
            
            return True
            
        except Exception as e:
            print(f"Error adding custom sticker: {e}")
            return False


# Global library instance
_sticker_library = None

def get_sticker_library():
    """Get singleton instance of StickerLibrary"""
    global _sticker_library
    if _sticker_library is None:
        _sticker_library = StickerLibrary()
    return _sticker_library


class StickerManager:
    """Manages sticker/watermark overlay operations"""
    
    POSITIONS = {
        "Góc phải dưới": "bottom_right",
        "Góc phải trên": "top_right", 
        "Góc trái dưới": "bottom_left",
        "Góc trái trên": "top_left",
        "Chính giữa (Center)": "center"
    }
    
    def __init__(self):
        self.sticker_cache = {}
    
    def load_sticker(self, sticker_path):
        """Load and cache sticker image with transparency support
        
        Args:
            sticker_path: Path to sticker image file (PNG/JPG)
            
        Returns:
            PIL Image object with RGBA mode, or None if failed
        """
        if not sticker_path or not os.path.exists(sticker_path):
            return None
            
        # Check cache
        if sticker_path in self.sticker_cache:
            return self.sticker_cache[sticker_path]
        
        try:
            img = Image.open(sticker_path)
            
            # Convert to RGBA for transparency support
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            self.sticker_cache[sticker_path] = img
            return img
            
        except Exception as e:
            print(f"Error loading sticker: {e}")
            return None
    
    def calculate_position(self, video_width, video_height, sticker_width, sticker_height, position_key):
        """Calculate sticker position coordinates
        
        Args:
            video_width: Width of video frame
            video_height: Height of video frame
            sticker_width: Width of sticker
            sticker_height: Height of sticker
            position_key: Position name (Vietnamese)
            
        Returns:
            Tuple of (x, y) coordinates for top-left corner of sticker
        """
        position = self.POSITIONS.get(position_key, "bottom_right")
        
        # Padding from edges (10% of smaller dimension)
        padding = min(video_width, video_height) // 20
        
        if position == "bottom_right":
            x = video_width - sticker_width - padding
            y = video_height - sticker_height - padding
            
        elif position == "top_right":
            x = video_width - sticker_width - padding
            y = padding
            
        elif position == "bottom_left":
            x = padding
            y = video_height - sticker_height - padding
            
        elif position == "top_left":
            x = padding
            y = padding
            
        elif position == "center":
            x = (video_width - sticker_width) // 2
            y = (video_height - sticker_height) // 2
        
        else:
            # Default to bottom right
            x = video_width - sticker_width - padding
            y = video_height - sticker_height - padding
        
        # Ensure coordinates are within bounds
        x = max(0, min(x, video_width - sticker_width))
        y = max(0, min(y, video_height - sticker_height))
        
        return (x, y)
    
    def resize_sticker(self, sticker_img, video_width, video_height, scale_factor):
        """Resize sticker based on video dimensions and scale factor
        
        Args:
            sticker_img: PIL Image object
            video_width: Width of video frame
            video_height: Height of video frame
            scale_factor: Scale as percentage of video size (0.05 - 0.5)
            
        Returns:
            Resized PIL Image object
        """
        if not sticker_img:
            return None
        
        # Calculate target size based on video dimensions
        # Use the smaller dimension as reference
        ref_size = min(video_width, video_height)
        target_size = int(ref_size * scale_factor)
        
        # Maintain aspect ratio
        orig_w, orig_h = sticker_img.size
        aspect_ratio = orig_w / orig_h
        
        if orig_w > orig_h:
            new_w = target_size
            new_h = int(target_size / aspect_ratio)
        else:
            new_h = target_size
            new_w = int(target_size * aspect_ratio)
        
        # Ensure minimum size
        new_w = max(10, new_w)
        new_h = max(10, new_h)
        
        return sticker_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    def apply_sticker_to_frame(self, frame, sticker_path, position_key, scale_factor):
        """Apply sticker overlay to a video frame
        
        Args:
            frame: OpenCV frame (numpy array, BGR)
            sticker_path: Path to sticker image
            position_key: Position name (Vietnamese)
            scale_factor: Scale factor (0.05 - 0.5)
            
        Returns:
            Frame with sticker applied (numpy array, BGR)
        """
        if not sticker_path or not os.path.exists(sticker_path):
            return frame
        
        try:
            # Load sticker
            sticker = self.load_sticker(sticker_path)
            if not sticker:
                return frame
            
            # Get frame dimensions
            frame_h, frame_w = frame.shape[:2]
            
            # Resize sticker
            sticker_resized = self.resize_sticker(sticker, frame_w, frame_h, scale_factor)
            if not sticker_resized:
                return frame
            
            sticker_w, sticker_h = sticker_resized.size
            
            # Calculate position
            x, y = self.calculate_position(frame_w, frame_h, sticker_w, sticker_h, position_key)
            
            # Convert PIL to OpenCV format
            sticker_cv = cv2.cvtColor(np.array(sticker_resized), cv2.COLOR_RGBA2BGRA)
            
            # Extract alpha channel
            alpha = sticker_cv[:, :, 3] / 255.0
            
            # Get the region of interest (ROI) from the frame
            y1, y2 = y, y + sticker_h
            x1, x2 = x, x + sticker_w
            
            # Ensure we don't go out of bounds
            if y2 > frame_h:
                y2 = frame_h
                sticker_cv = sticker_cv[:y2-y, :, :]
                alpha = alpha[:y2-y, :]
            
            if x2 > frame_w:
                x2 = frame_w
                sticker_cv = sticker_cv[:, :x2-x, :]
                alpha = alpha[:, :x2-x]
            
            roi = frame[y1:y2, x1:x2]
            
            # Blend using alpha channel
            for c in range(3):  # BGR channels
                roi[:, :, c] = (alpha * sticker_cv[:, :, c] + 
                               (1 - alpha) * roi[:, :, c])
            
            # Put ROI back into frame
            frame[y1:y2, x1:x2] = roi
            
            return frame
            
        except Exception as e:
            print(f"Error applying sticker: {e}")
            return frame
    
    def generate_ffmpeg_overlay_filter(self, sticker_path, video_width, video_height, 
                                      position_key, scale_factor):
        """Generate FFmpeg overlay filter string for hardware-accelerated processing
        
        Args:
            sticker_path: Path to sticker image
            video_width: Width of video
            video_height: Height of video
            position_key: Position name
            scale_factor: Scale factor
            
        Returns:
            FFmpeg filter string, or None if invalid
        """
        if not sticker_path or not os.path.exists(sticker_path):
            return None
        
        try:
            # Load to get dimensions
            sticker = self.load_sticker(sticker_path)
            if not sticker:
                return None
            
            # Calculate scaled size
            sticker_resized = self.resize_sticker(sticker, video_width, video_height, scale_factor)
            sticker_w, sticker_h = sticker_resized.size
            
            # Calculate position
            x, y = self.calculate_position(video_width, video_height, sticker_w, sticker_h, position_key)
            
            # Build FFmpeg overlay filter
            # Format: [0:v][1:v]overlay=x:y[out]
            # We need to scale the overlay first
            filter_str = f"[1:v]scale={sticker_w}:{sticker_h}[ovrl];[0:v][ovrl]overlay={x}:{y}"
            
            return filter_str
            
        except Exception as e:
            print(f"Error generating FFmpeg filter: {e}")
            return None
    
    def clear_cache(self):
        """Clear sticker cache to free memory"""
        self.sticker_cache.clear()


# Singleton instance
_sticker_manager = None

def get_sticker_manager():
    """Get singleton instance of StickerManager"""
    global _sticker_manager
    if _sticker_manager is None:
        _sticker_manager = StickerManager()
    return _sticker_manager


# Convenience functions for direct use
def apply_sticker(frame, sticker_path, position="Góc phải dưới", scale=0.2):
    """Convenience function to apply sticker to frame
    
    Args:
        frame: OpenCV frame (BGR)
        sticker_path: Path to sticker image
        position: Position name (default: bottom right)
        scale: Scale factor (default: 0.2 = 20%)
        
    Returns:
        Frame with sticker applied
    """
    manager = get_sticker_manager()
    return manager.apply_sticker_to_frame(frame, sticker_path, position, scale)

def fixconflict():
    """Fix conflict between tkinter and tkinterdnd2"""
    if TKDND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
def get_ffmpeg_overlay_filter(sticker_path, video_width, video_height, 
                               position="Góc phải dưới", scale=0.2):
    """Convenience function to get FFmpeg overlay filter
    
    Args:
        sticker_path: Path to sticker image
        video_width: Video width
        video_height: Video height
        position: Position name
        scale: Scale factor
        
    Returns:
        FFmpeg filter string
    """
    manager = get_sticker_manager()
    return manager.generate_ffmpeg_overlay_filter(
        sticker_path, video_width, video_height, position, scale
    )
