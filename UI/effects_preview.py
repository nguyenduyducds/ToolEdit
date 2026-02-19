# Realtime Effects Preview
# Applies all visual effects to preview frames

import cv2
import numpy as np
from PIL import Image as PILImage
import os


def apply_realtime_effects(main_window, frame):
    """
    Apply all realtime effects to a video frame using OpenCL (cv2.UMat) for GPU acceleration
    Returns: processed frame ready for display (RGB format)
    """
    
    # 1. Convert to UMat (OpenCL) -> GPU Memory
    u_frame = cv2.UMat(frame)
    
    # 2. Resize to preview quality (480p)
    h_base, w_base = frame.shape[:2]
    proc_h = 480
    
    if h_base > proc_h:
        scale = proc_h / h_base
        proc_w = int(w_base * scale)
        if proc_w > 1280:
            scale = 1280 / w_base
            proc_w = 1280
            proc_h = int(h_base * scale)
        
        frame_base = cv2.resize(u_frame, (proc_w, proc_h), interpolation=cv2.INTER_LINEAR)
    else:
        frame_base = u_frame
        proc_w, proc_h = w_base, h_base

    # 3. Determine Canvas Size
    ratio_str = main_window.aspect_ratio.get()
    
    target_ratio = None
    if "9:16" in ratio_str: target_ratio = 9/16
    elif "16:9" in ratio_str: target_ratio = 16/9
    elif "1:1" in ratio_str: target_ratio = 1.0
    elif "4:3" in ratio_str: target_ratio = 4/3
    
    if target_ratio is None:
        target_ratio = proc_w / proc_h

    # Calculate Canvas dimensions
    if target_ratio < 1.0:  # Portrait
        c_h = proc_h
        c_w = int(proc_h * target_ratio)
    else:  # Landscape or Square
        c_w = proc_w
        c_h = int(proc_w / target_ratio)
    
    # 4. Create Background (OpenCL Accelerated Blur)
    if main_window.enable_blur.get() and main_window.blur_amount.get() > 0:
        blur_val = main_window.blur_amount.get()
        blur_downscale = 2
        blur_w = c_w // blur_downscale
        blur_h = c_h // blur_downscale
        
        # Downscale & Blur on GPU
        bg_small = cv2.resize(frame_base, (blur_w, blur_h), interpolation=cv2.INTER_LINEAR)
        k = int(blur_val * 3) * 2 + 1
        if k > 1:
            bg_blurred = cv2.GaussianBlur(bg_small, (k, k), 0)
        else:
            bg_blurred = bg_small
        
        # Upscale
        canvas = cv2.resize(bg_blurred, (c_w, c_h), interpolation=cv2.INTER_LINEAR)
    else:
        # Create black canvas (UMat)
        # Note: cv2.UMat does not support np.zeros directly easily, 
        # but we can create numpy zeros and convert, OR just use resize from a black source?
        # Cleanest: Create numpy zeros then convert. Overheads are small for single frame creation.
        canvas_np = np.zeros((c_h, c_w, 3), dtype=np.uint8)
        canvas = cv2.UMat(canvas_np)

    # 5. Prepare Foreground
    scale_fit_preview = min(c_w / w_base, c_h / h_base)
    w_fitted = w_base * scale_fit_preview
    h_fitted = h_base * scale_fit_preview
    
    s_w = main_window.scale_w.get()
    s_h = main_window.scale_h.get()
    
    new_scaled_w = max(1, int(w_fitted * s_w))
    new_scaled_h = max(1, int(h_fitted * s_h))
    
    frame_fg = cv2.resize(frame_base, (new_scaled_w, new_scaled_h), interpolation=cv2.INTER_LINEAR)
    
    # Apply Color Filter (UMat compatible)
    frame_fg = apply_color_filter(main_window, frame_fg)
    
    # Apply Brightness
    frame_fg = apply_brightness(main_window, frame_fg)
    
    # Mirror
    if main_window.mirror_enabled.get():
        frame_fg = cv2.flip(frame_fg, 1)

    # 6. Composition (Paste FG onto BG)
    # Convert back to Numpy for complex slicing/indexing (OpenCV UMat slicing is limited/tricky)
    # Getting data back from GPU to CPU here is necessary for pixel-precise compositing if UMat slicing fails,
    # but let's try to keep it efficiently.
    # Actually, simplest reliability upgrade is: Process heavy transforms (resize/blur/color) on GPU/UMat,
    # then bring back to CPU for final composition.
    
    canvas_cpu = canvas.get() # Download from GPU
    frame_fg_cpu = frame_fg.get() # Download from GPU
    
    y_off = (c_h - new_scaled_h) // 2
    x_off = (c_w - new_scaled_w) // 2

    y1, y2 = max(0, y_off), min(c_h, y_off + new_scaled_h)
    x1, x2 = max(0, x_off), min(c_w, x_off + new_scaled_w)
    
    sy1, sy2 = max(0, -y_off), max(0, -y_off) + (y2 - y1)
    sx1, sx2 = max(0, -x_off), max(0, -x_off) + (x2 - x1)

    if (y2 > y1) and (x2 > x1):
         canvas_cpu[y1:y2, x1:x2] = frame_fg_cpu[sy1:sy2, sx1:sx2]
    
    # 7. Subtitle Bar & Sticker (CPU operations are fast enough for overlay)
    canvas_cpu = apply_subtitle_bar(main_window, canvas_cpu, c_h, c_w)
    canvas_cpu = apply_sticker_overlay(main_window, canvas_cpu, c_h, c_w)
    
    # 8. RGB Convert (CPU or GPU? CPU is fine here as we are already on CPU)
    # Could move back to GPU for CVTColor but transfer cost might outweigh.
    final_frame = cv2.cvtColor(canvas_cpu, cv2.COLOR_BGR2RGB)
    
    return final_frame


def apply_color_filter(main_window, frame):
    """Apply color filter to frame (OpenCL optimized)"""
    color_filter = main_window.color_filter.get()
    if not color_filter or "None" in color_filter or "Gốc" in color_filter:
        return frame
    
    # Note: 'frame' here is likely a UMat from the caller
    
    if "Đen Trắng" in color_filter or "B&W" in color_filter:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
    elif "Sepia" in color_filter or "Cổ điển" in color_filter:
        # Sepia matrix
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        # cv2.transform supports UMat
        frame = cv2.transform(frame, kernel)
        
    elif "Vintage" in color_filter or "Phim cũ" in color_filter:
        # Vintage effect (Desaturate + Tint)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Split channels: UMat does not support direct indexing like hsv[:,:,1]
        h, s, v = cv2.split(hsv)
        
        # Desaturate: s * 0.8
        s = cv2.multiply(s, 0.8) # UMat safe
        
        hsv = cv2.merge([h, s, v])
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Tint channels: R*1.1, G*1.0, B*0.9 (approx vintage)
        b, g, r = cv2.split(frame)
        b = cv2.multiply(b, 0.9)
        r = cv2.multiply(r, 1.1)
        # Recast to prevent overflow quirks (though multiply handles it usually)
        frame = cv2.merge([b, g, r])
        
    elif "Cold" in color_filter or "Lạnh" in color_filter:
        # Boost Blue, Reduce Red
        b, g, r = cv2.split(frame)
        b = cv2.multiply(b, 1.3)
        r = cv2.multiply(r, 0.8)
        frame = cv2.merge([b, g, r])
        
    elif "Warm" in color_filter or "Ấm" in color_filter:
        # Boost Red, Reduce Blue
        b, g, r = cv2.split(frame)
        b = cv2.multiply(b, 0.7)
        r = cv2.multiply(r, 1.3)
        frame = cv2.merge([b, g, r])
    
    return frame


def apply_brightness(main_window, frame):
    """Apply brightness adjustment (OpenCL compatible)"""
    if main_window.enable_brightness.get():
        brightness = main_window.brightness.get()
        if brightness != 1.0:
            # Alpha=contrast check, Beta=brightness.
            # Here user wants "brightness" multiplier style.
            # cv2.convertScaleAbs(frame, alpha=brightness, beta=0) is perfect for this.
            # It performs: out = frame * alpha + beta
            frame = cv2.convertScaleAbs(frame, alpha=brightness, beta=0)
    return frame


def apply_subtitle_bar(main_window, canvas, c_h, c_w):
    """Draw subtitle black bar"""
    if main_window.enable_subtitle_bar.get():
        bar_height_px = main_window.subtitle_bar_height.get()
        bar_height_preview = int(bar_height_px * (c_h / 1280.0))
        bar_height_preview = min(bar_height_preview, c_h // 3)
        
        if bar_height_preview > 0:
            cv2.rectangle(canvas, 
                        (0, c_h - bar_height_preview),
                        (c_w, c_h),
                        (0, 0, 0),
                        -1)
    return canvas


# Cache for sticker to avoid reloading every frame (HUGE performance boost)
_sticker_cache = {
    'path': None,
    'scale': None,
    'canvas_size': None,
    'sticker_rgba': None,  # Pre-processed RGBA
    'sticker_bgr': None,   # BGR channels
    'sticker_alpha': None  # Alpha mask (pre-normalized)
}

def apply_sticker_overlay(main_window, canvas, c_h, c_w):
    """Overlay sticker on canvas (OPTIMIZED - No lag!)"""
    if not main_window.enable_sticker.get():
        return canvas
    
    sticker_path = main_window.sticker_path.get()
    if not sticker_path or not os.path.exists(sticker_path):
        return canvas
    
    try:
        sticker_scale = main_window.sticker_scale.get()
        cache_key = (sticker_path, sticker_scale, c_w, c_h)
        
        # Check cache - Only reload if path/scale/size changed
        if (_sticker_cache['path'] != sticker_path or 
            _sticker_cache['scale'] != sticker_scale or
            _sticker_cache['canvas_size'] != (c_w, c_h)):
            
            # Load and process sticker (only when needed)
            sticker_pil = PILImage.open(sticker_path)
            
            if sticker_pil.mode != 'RGBA':
                sticker_pil = sticker_pil.convert('RGBA')
            
            sticker_w = int(c_w * sticker_scale)
            sticker_h = int(sticker_w * (sticker_pil.height / sticker_pil.width))
            
            sticker_pil = sticker_pil.resize((sticker_w, sticker_h), PILImage.Resampling.LANCZOS)
            sticker_rgba = np.array(sticker_pil)
            
            # Pre-process for fast blending
            if sticker_rgba.shape[2] == 4:
                # Convert RGBA to BGR (OpenCV format)
                sticker_bgr = cv2.cvtColor(sticker_rgba, cv2.COLOR_RGBA2BGR)
                # Pre-normalize alpha to 0-1 range
                sticker_alpha = sticker_rgba[:, :, 3:4].astype(np.float32) / 255.0
            else:
                sticker_bgr = cv2.cvtColor(sticker_rgba, cv2.COLOR_RGB2BGR)
                sticker_alpha = None
            
            # Update cache
            _sticker_cache['path'] = sticker_path
            _sticker_cache['scale'] = sticker_scale
            _sticker_cache['canvas_size'] = (c_w, c_h)
            _sticker_cache['sticker_bgr'] = sticker_bgr
            _sticker_cache['sticker_alpha'] = sticker_alpha
        
        # Use cached sticker
        sticker_bgr = _sticker_cache['sticker_bgr']
        sticker_alpha = _sticker_cache['sticker_alpha']
        sticker_h, sticker_w = sticker_bgr.shape[:2]
        
        # Calculate position
        sticker_pos = main_window.sticker_pos.get()
        margin = 20
        
        if "Tùy chỉnh" in sticker_pos or "Custom" in sticker_pos:
            x_pos = int(main_window.sticker_drag_x.get() * c_w)
            y_pos = int(main_window.sticker_drag_y.get() * c_h)
        else:
            x_pos = c_w - sticker_w - margin
            y_pos = c_h - sticker_h - margin
            
            if "trái" in sticker_pos or "Left" in sticker_pos:
                x_pos = margin
            if "trên" in sticker_pos or "Top" in sticker_pos:
                y_pos = margin
            if "giữa" in sticker_pos or "Center" in sticker_pos:
                x_pos = (c_w - sticker_w) // 2
                y_pos = (c_h - sticker_h) // 2
        
        x_pos = max(0, min(x_pos, c_w - sticker_w))
        y_pos = max(0, min(y_pos, c_h - sticker_h))
        
        y1, y2 = y_pos, y_pos + sticker_h
        x1, x2 = x_pos, x_pos + sticker_w
        
        # Bounds check
        if y2 > c_h or x2 > c_w:
            return canvas
        
        # OPTIMIZED Alpha blending using NumPy vectorization (100x faster!)
        if sticker_alpha is not None:
            # Vectorized operation - No Python loops!
            roi = canvas[y1:y2, x1:x2].astype(np.float32)
            blended = sticker_alpha * sticker_bgr.astype(np.float32) + (1 - sticker_alpha) * roi
            canvas[y1:y2, x1:x2] = blended.astype(np.uint8)
        else:
            # No alpha - Direct paste
            canvas[y1:y2, x1:x2] = sticker_bgr
    
    except Exception as e:
        pass
    
    return canvas
