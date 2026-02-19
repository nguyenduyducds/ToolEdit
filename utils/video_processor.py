"""Video processing utilities - Pure functions without UI dependencies"""

import os
import sys
import subprocess
import threading
import shutil
import shutil
from pathlib import Path
import queue
import multiprocessing
import psutil # For priority management

# Global lock for intro/outro concat (prevent race conditions)
CONCAT_LOCK = threading.Lock()


def process_video_with_ffmpeg(input_path, output_path, settings, srt_file=None, log_callback=None, progress_callback=None, check_stop_signal=None):
    """
    Process video entirely with FFmpeg - ULTRA FAST
    
    Args:
        input_path: Input video path
        output_path: Output video path
        settings: Dict with video settings (blur, brightness, zoom, speed, etc.)
        srt_file: Optional SRT subtitle file path
        log_callback: Optional callback function for logging
        progress_callback: Optional callback function for progress updates (0-100)
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Determine FFmpeg path (Priority: Local > Bin > ImageIO > System)
    ffmpeg_path = "ffmpeg"
    
    # Check local folder (for portable/exe)
    local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg.exe")
    bin_ffmpeg = os.path.join(os.getcwd(), "bin", "ffmpeg.exe")
    
    if os.path.exists(local_ffmpeg):
        ffmpeg_path = local_ffmpeg
    elif os.path.exists(bin_ffmpeg):
        ffmpeg_path = bin_ffmpeg
    else:
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            ffmpeg_path = get_ffmpeg_exe()
        except:
            pass
            
    # Also check for bundled ffmpeg in PyInstaller temp dir
    if getattr(sys, 'frozen', False):
        bundled_ffmpeg = os.path.join(sys._MEIPASS, "ffmpeg.exe")
        if os.path.exists(bundled_ffmpeg):
            ffmpeg_path = bundled_ffmpeg
    
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    # Build FFmpeg filter chain
    filters = []
    
    # Extract settings
    start_time = settings.get('start_time', 0)
    duration = settings.get('duration', 120)
    blur_amount = settings.get('blur_amount', 0)
    brightness = settings.get('brightness', 1.0)
    zoom_factor = settings.get('zoom_factor', 1.0)
    speed_factor = settings.get('speed_factor', 1.0)
    mirror_enabled = settings.get('mirror_enabled', False)
    convert_to_portrait = settings.get('convert_to_portrait', False)
    simple_mode = settings.get('simple_mode', False)
    use_gpu = settings.get('use_gpu', True)
    
    # Subtitle settings
    subtitle_font_size = settings.get('subtitle_font_size', 14)
    subtitle_color = settings.get('subtitle_color', 'FFFFFF')
    subtitle_outline = settings.get('subtitle_outline', 3)
    
    # 1. Trim video
    start_str = f"-ss {start_time}"
    duration_str = f"-t {duration}"
    
    # 2. Speed
    enable_speed = settings.get('enable_speed', True)
    if enable_speed and speed_factor != 1.0:
        filters.append(f"setpts={1/speed_factor}*PTS")
    
    # 3. Mirror
    if mirror_enabled:
        filters.append("hflip")
    
    # 4. Blur (Disabled - moved to Background Blur logic)
    # enable_blur = settings.get('enable_blur', True)
    # if enable_blur and blur_amount > 0:
    #     filters.append(f"boxblur={blur_amount}:{blur_amount}")
    
    # 5. Brightness
    enable_brightness = settings.get('enable_brightness', True)
    if enable_brightness and brightness != 1.0:
        filters.append(f"eq=brightness={brightness-1.0}")
    
    # 6. Subtitles
    # TEMPORARY: Disable subtitles when blur background is enabled (filter chain conflict)
    enable_blur_check = settings.get('enable_blur', False)
    blur_amount_check = settings.get('blur_amount', 0)
    
    subtitle_cmd = None
    if srt_file and os.path.exists(srt_file):
        # Use Absolute Path and Escape for FFmpeg Filter
        abs_srt_path = os.path.abspath(srt_file)
        # Windows path: C:\path\to\file -> C\:/path/to/file (FFmpeg filter syntax)
        # Escape colon to prevent it being treated as option separator
        srt_escaped = abs_srt_path.replace('\\', '/').replace(':', '\\:')
        
        subtitle_cmd = f"subtitles=filename='{srt_escaped}':force_style='FontSize={subtitle_font_size},PrimaryColour=&H{subtitle_color},OutlineColour=&H000000,Outline={subtitle_outline},Bold=1,Alignment=2'"

    # 7. Scale (Transform Layer) - READ ONLY here, apply later
    scale_w = float(settings.get('scale_w', 1.0))
    scale_h = float(settings.get('scale_h', 1.0))
    
    # MOVED: filters.append(f"scale=iw*{scale_w}:ih*{scale_h}") 
    # Reason: We need to apply scale differently for BG and FG in Blur mode.
        
    # 7b. Color Filters (NEW)
    color_filter = settings.get('color_filter', 'None')
    c_cmd = "" # Initialize here to prevent NameError later
    if color_filter and "None" not in color_filter:
        if "Đen Trắng" in color_filter or "B&W" in color_filter: 
            c_cmd = "hue=s=0"
        elif "Sepia" in color_filter or "Cổ điển" in color_filter: 
            c_cmd = "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131"
        elif "Vintage" in color_filter or "Phim cũ" in color_filter: 
            c_cmd = "eq=contrast=1.1:brightness=-0.05:saturation=0.8,colorbalance=rs=0.1:gs=-0.05:bs=-0.1"
        elif "Cold" in color_filter or "Lạnh" in color_filter: 
            c_cmd = "colorbalance=rs=-0.2:gs=-0.1:bs=0.3,eq=saturation=1.2"
        elif "Warm" in color_filter or "Ấm" in color_filter: 
            c_cmd = "colorbalance=rs=0.3:gs=-0.1:bs=-0.3,eq=saturation=1.1"
        elif "Vivid" in color_filter or "Rực rỡ" in color_filter:
            c_cmd = "eq=saturation=1.5:contrast=1.1"
        elif "Cinematic" in color_filter or "Điện ảnh" in color_filter:
            # Teal & Orange look
            c_cmd = "colorbalance=rs=-0.1:bs=0.2:rh=0.2:bh=-0.1,eq=contrast=1.1:saturation=1.1"
        elif "Dreamy" in color_filter or "Mộng mơ" in color_filter:
            c_cmd = "colorbalance=rs=0.1:bs=0.1,eq=contrast=0.9:brightness=0.05:saturation=0.8"
        elif "Dramatic" in color_filter or "Kịch tính" in color_filter:
            c_cmd = "eq=contrast=1.3:saturation=0.6:brightness=-0.05"
        elif "Cyberpunk" in color_filter:
            # Neon Blue/Purple vibe
            c_cmd = "colorbalance=rs=-0.2:gs=-0.1:bs=0.4:rh=0.2:gh=-0.1:bh=0.2,eq=contrast=1.2:saturation=1.4"
        if c_cmd:
            filters.append(c_cmd)
        
    # 7c. Subtitle Bar (Black Box)
    drawbox_filter = None
    if settings.get('enable_subtitle_bar', False): # Correct key name
        bar_h = int(settings.get('subtitle_bar_height', 80))
        # Draw black box at bottom (y=ih-h)
        drawbox_filter = f"drawbox=y=ih-{bar_h}:color=black@1.0:t=fill"

    # 7d. Text Outro (NEW)
    text_outro_filter = None
    if settings.get('enable_outro_text', False):
        content = settings.get('outro_text_content', '')
        end_dur = int(settings.get('outro_text_duration', 5))
        
        if content:
            # Calculate ACTUAL video duration after trimming
            start_time_val = settings.get('start_time', 0)
            duration_val = settings.get('duration', 0)
            
            # If duration is 0, it means "full video from start_time to end"
            if duration_val == 0:
                # Probe original video duration
                info = get_video_info(input_path)
                if info:
                    original_duration = info.get('duration', 0)
                    # Actual duration = original - start_time
                    total_dur = max(0, original_duration - start_time_val)
                else:
                    total_dur = 0
            else:
                # Use specified duration
                total_dur = duration_val
            
            if total_dur > 0:
                start_t = max(0, total_dur - end_dur)
                
                # Basic escaping for FFmpeg drawtext
                # Escape: ' -> \', : -> \:
                safe_content = content.replace("'", "'\''").replace(":", "\:")
                
                # Font selection
                font_name = settings.get('outro_text_font', 'Arial (Mặc định)')
                font_path = "C:/Windows/Fonts/arial.ttf" # Default
                
                # Map names to Windows Font Paths
                font_map = {
                    "arial": "C:/Windows/Fonts/arial.ttf",
                    "segoe ui": "C:/Windows/Fonts/segoeui.ttf", 
                    "times new roman": "C:/Windows/Fonts/times.ttf",
                    "tahoma": "C:/Windows/Fonts/tahoma.ttf",
                    "verdana": "C:/Windows/Fonts/verdana.ttf",
                    "impact": "C:/Windows/Fonts/impact.ttf"
                }
                
                # Case insensitive match
                for key, path in font_map.items():
                    if key in font_name.lower():
                        font_path = path
                        break
                
                escaped_font_path = font_path.replace(':', '\\:')
                font_arg = f":fontfile='{escaped_font_path}'"
                
                # Get customizable settings
                fontsize = int(settings.get('outro_text_font_size', 60))
                fontcolor = settings.get('outro_text_font_color', 'white')
                
                # Position logic
                pos_mode = settings.get('outro_text_position', 'center')
                x_expr = "(w-text_w)/2"
                y_expr = "(h-text_h)/2"
                
                if pos_mode == 'top':
                    y_expr = "h/5"
                elif pos_mode == 'bottom':
                    y_expr = "h-h/5"
                
                # Box/Background logic - Build box parameters FIRST
                box_params = ""
                # User explicitly asked for "textbox màu đen", so we check the box boolean
                if settings.get('outro_text_box', False):
                    # Use selected bg color (default black) with some opacity
                    box_bg_color = settings.get('outro_text_bg_color', 'black')
                    padding = int(settings.get('outro_text_box_padding', 15))
                    
                    # DEBUG LOG
                    log(f"   [DEBUG] Text Box Enabled: bg={box_bg_color}, padding={padding}")
                    
                    if box_bg_color != 'transparent':
                        # FFmpeg drawtext box syntax: box=1 MUST come before fontcolor
                        # boxcolor format: color@opacity or just color
                        if '@' not in box_bg_color:
                            box_params = f"box=1:boxcolor={box_bg_color}@0.7:boxborderw={padding}:"
                        else:
                            box_params = f"box=1:boxcolor={box_bg_color}:boxborderw={padding}:"
                        
                        log(f"   [DEBUG] Box Params: {box_params}")
                
                # Draw Text: Box params FIRST, then text styling
                # Correct order: box -> fontfile -> fontsize -> fontcolor -> x -> y -> enable -> shadow
                text_outro_filter = (f"drawtext={box_params}text='{safe_content}'{font_arg}:fontsize={fontsize}:fontcolor={fontcolor}:"
                                     f"x={x_expr}:y={y_expr}:enable='between(t,{start_t},{total_dur})':"
                                     f"shadowcolor=black:shadowx=2:shadowy=2")
                
                # DEBUG: Log final filter
                log(f"   [DEBUG] Text Outro Filter: {text_outro_filter[:200]}...")



    # 8. Aspect Ratio (Smart Resize & Blur Background) & Sticker
    ratio_str = settings.get('aspect_ratio', 'Original')
    resize_mode = settings.get('resize_mode', 'Fit') # Fit or Fill
    simple_mode = settings.get('simple_mode', False)
    enable_blur = settings.get('enable_blur', False) # Check for BG Blur
    blur_amount = settings.get('blur_amount', 0)
    
    vf = None # Initialize vf safe fallback
    
    # Sticker Settings
    enable_sticker = settings.get('enable_sticker', False)
    sticker_path = settings.get('sticker_path', '')
    sticker_input_idx = 0 
    
    log(f"   [DEBUG] Received aspect_ratio: '{ratio_str}'")
    
    # --- LOGIC QUYẾT ĐỊNH FILTER ---
    use_complex_blur = (enable_blur and blur_amount > 0)
    
    # 1. Xác định Canvas
    # (Giữ logic cũ)
    if "9:16" in ratio_str: target_w, target_h = 1080, 1920
    elif "1:1" in ratio_str: target_w, target_h = 1080, 1080
    elif "4:3" in ratio_str: target_w, target_h = 1440, 1080
    elif "16:9" in ratio_str: target_w, target_h = 1920, 1080
    else: 
        # --- AUTO DETECT (Original) ---
        try:
             # Use the improved get_video_info that handles rotation
             info_probe = get_video_info(input_path)
             if info_probe and info_probe.get('width') and info_probe.get('height'):
                 target_w = info_probe['width']
                 target_h = info_probe['height']
                 # Ensure dimensions are even
                 target_w = (target_w // 2) * 2
                 target_h = (target_h // 2) * 2
                 
                 log(f"   [DEBUG] Detected Original Resolution: {target_w}x{target_h}")
             else:
                 # Smarter Fallback: If "Original" but probe failed, 
                 # we don't want to force 1280x720 because it ruins vertical videos.
                 # Let's use 0,0 and disable complex parts that need exact W/H
                 if "Original" in ratio_str:
                     target_w, target_h = 0, 0
                     use_complex_blur = False
                 else:
                     target_w, target_h = 1280, 720 # Generic fallback
        except Exception as e:
             log(f"   [DEBUG] Resolution detection failed: {e}")
             if "Original" in ratio_str:
                 target_w, target_h = 0, 0
                 use_complex_blur = False
             else:
                 target_w, target_h = 1280, 720
             
        if not use_complex_blur:
            # For simple mode (no background blur), we usually rely on 'scale=-2:720' or similar.
            # But since we now have exact W/H, we can pass that through or ignore it 
            # as the later logic for 'Original' handles iw/ih.
            pass

    # 2. Xây dựng Filter Chain (Updated with User Scale)
    if use_complex_blur:
        # --- CHẾ ĐỘ NỀN MỜ ---
        log(f"   [DEBUG] Mode: Complex Blur with Scaled FG")
        
        b_val = int(blur_amount)
        if not simple_mode:
            # --- OPTIMIZED BLUR BACKGROUND ---
            # Strategy: Downscale -> Blur -> Upscale
            # This is 10-20x faster than blurring HD video directly
            low_res_w = 64 # Very small width for fast blur
            
            # 1. Split [0:v] into [bg_raw] and [fg]
            # 2. [bg_raw] -> scale low res -> crop -> boxblur -> scale back up -> [bg_blur]
            # 3. [fg] -> scale/resize -> [fg_sized]
            # 4. [bg_blur][fg_sized]overlay
            
            # Ensure Even Dimensions for Low Res (YUV requirement)
            lr_h = int(low_res_w * target_h / target_w)
            if lr_h % 2 != 0: lr_h += 1

            # Note: We use scale parameters to ensure correct aspect ratio filling
            # PRE-PROCESS FILTERS: Join all simple filters (speed, mirror, color, brightness)
            pre_filters = ','.join(filters) + ',' if filters else ''
            
            vf = (
                f"[0:v]format=yuv420p,{pre_filters}split=2[bg_raw][fg];"
                # Process Background:
                # 1. Calc low res height based on target aspect ratio to maintain shape
                # 2. Scale 'increase' to cover the low_res box (prevents invalid crop on landscape input)
                # 3. Crop -> Blur -> Scale Up
                f"[bg_raw]scale={low_res_w}:{lr_h}:force_original_aspect_ratio=increase,"
                f"crop={low_res_w}:{lr_h},boxblur={blur_amount}:2,"
                f"scale={target_w}:{target_h}:flags=bilinear,setsar=1[bg_blur];"
                # Process Foreground:
                # Force Even Dimensions for FG Scaling using trunc expression
                f"[fg]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
                f"scale=trunc(iw*{scale_w:.4f}/2)*2:trunc(ih*{scale_h:.4f}/2)*2,setsar=1[fg_sized];"
                # Overlay - Final setsar=1 safety net AND FORCE OUTPUT SIZE
                f"[bg_blur][fg_sized]overlay=(W-w)/2:(H-h)/2:shortest=1,scale={target_w}:{target_h},setsar=1[v_main]"
            )
            has_complex_filter = True
            filters = [] # Clear filters so they are not appended again or overwrite vf later
        else:
            if b_val < 1: b_val = 1
            
            pre = f"[0:v]{','.join(filters)},format=yuv420p" if filters else "[0:v]format=yuv420p"
            
            # NOTE: [bg] does NOT get user scale (it should fill canvas). [fg] gets user scale.
            complex_part = (
                f"{pre},split=2[bg][fg];"
                f"[bg]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},boxblur={b_val*2}:{b_val}[bg_blur];"
                # FG Logic: Fit to canvas -> Apply User Scale
                f"[fg]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,scale=trunc(iw*{scale_w:.4f}/2)*2:trunc(ih*{scale_h:.4f}/2)*2[fg_sized];"
                f"[bg_blur][fg_sized]overlay=(W-w)/2:(H-h)/2:shortest=1,setsar=1[v_main]"
            )
            filters = [complex_part] # Replace chain
            has_complex_filter = True  # Mark as complex filter
        
    elif "Fill" in resize_mode and not "Original" in ratio_str:
        # --- CROP/FILL ---
        # Apply Zoom/Scale BEFORE Crop? Or After? 
        # Usually Zoom implies zooming into the video. So scale first.
        if scale_w != 1.0 or scale_h != 1.0:
             filters.append(f"scale=trunc(iw*{scale_w:.4f}/2)*2:trunc(ih*{scale_h:.4f}/2)*2")
             
        filters.append(f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase")
        filters.append(f"crop={target_w}:{target_h}")
        
    elif "Original" in ratio_str:
        # --- ORIGINAL ---
        # Keep source resolution but ensure even dimensions (Required for H.264/HEVC)
        # setsar=1 ensures square pixels to avoid display distortion
        filters.append("scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1")
        
        # Apply user zoom/scale if specified
        if scale_w != 1.0 or scale_h != 1.0:
            filters.append(f"scale=trunc(iw*{scale_w:.4f}/2)*2:trunc(ih*{scale_h:.4f}/2)*2")
            
        # Force standard pixel format for compatibility (Fixes 'video gốc' issues)
        filters.append("format=yuv420p")
        
    else:
        # --- FIT (Safe Zoom with Overlay) OR PAD (Faster) ---
        # If no zoom/scale and Simple Mode, use PAD for speed
        if simple_mode and scale_w == 1.0 and scale_h == 1.0:
            pre = f"[0:v]{','.join(filters)}," if filters else "[0:v]"
            # Pad logic: Scale decreasing to fit, then Pad with black
            complex_part = (
                 f"{pre}format=yuv420p,scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
                 f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v_main]"
            )
            filters = [complex_part] # Replace chain
            has_complex_filter = True
        else:
            # ORIGINAL OVERLAY LOGIC (Better for Zooming/Moving)
            # Instead of 'pad' (which crashes if content > canvas during zoom), 
            # we generate a Black Background and Overlay the fitted video on top.
            
            # 1. Join exiting filters into pre-chain
            pre = f"[0:v]{','.join(filters)}," if filters else "[0:v]"
            
            # 2. Build Complex Filter
            # Force BG dimensions to be even
            target_w_even = (target_w // 2) * 2
            target_h_even = (target_h // 2) * 2
            
            complex_part = (
                f"color=c=black:s={target_w_even}x{target_h_even}[bg];"
                f"{pre}format=yuv420p,scale={target_w_even}:{target_h_even}:force_original_aspect_ratio=decrease,"
                f"scale=trunc(iw*{scale_w:.4f}/2)*2:trunc(ih*{scale_h:.4f}/2)*2,setsar=1[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,setsar=1[v_main]"
            )
            
            filters = [complex_part] # Replace chain
            has_complex_filter = True
                
    # MULTIPLE STICKERS LOGIC (NEW - CapCut Style)
    stickers_list = settings.get('stickers_list', [])
    enable_sticker = settings.get('enable_sticker', False)
    
    # Fallback to legacy single sticker if stickers_list is empty
    if enable_sticker and not stickers_list:
        sticker_path = settings.get('sticker_path', '')
        if sticker_path and os.path.exists(sticker_path):
            stickers_list = [{
                'path': sticker_path,
                'pos': settings.get('sticker_pos', 'Góc phải dưới'),
                'scale': settings.get('sticker_scale', 0.2),
                'x': settings.get('sticker_drag_x', 0.8),
                'y': settings.get('sticker_drag_y', 0.8)
            }]
    
    
    # Drawbox is now handled separately (see 7c logic)
    # No need to extract from filters list

    
    # Combine filters
    # Only overwrite vf if filters has content (don't clobber complex blur)
    if filters:
        vf = ','.join(filters)
    
    # Check if we already have a complex filter (from blur background)
    has_complex_filter = vf and (';' in vf or 'split[' in vf)
    
    # Process Multiple Stickers
    # Initialize output label variable in outer scope - CRITICAL for preventing UnboundLocalError
    final_output_label = None

    if enable_sticker and stickers_list:
        # Helper to format float to string for FFmpeg (avoid scientific notation)
        def flt(v): return "{:.4f}".format(float(v))
        
        # Build sticker overlay chain
        sticker_filters = []
        current_label = "v_main" if has_complex_filter or vf else "0:v"
        
        # If we have existing filters, label the output
        if has_complex_filter:
            # Complex filter already exists, just append
            pass
        elif vf:
            # Convert simple filter to complex
            vf = f"[0:v]{vf}[v_main]"
            has_complex_filter = True
        else:
            # No filters, start fresh
            vf = ""
            has_complex_filter = True
        
        # Add each sticker as overlay
        for i, sticker in enumerate(stickers_list):
            sticker_path = sticker.get('path', '')
            if not sticker_path or not os.path.exists(sticker_path):
                continue
            
            s_pos = sticker.get('pos', 'Góc phải dưới')
            s_scale = sticker.get('scale', 0.2)
            s_x = sticker.get('x', 0.0)
            s_y = sticker.get('y', 0.0)
            
            # Create unique labels
            stk_label = f"stk{i}"
            next_label = f"v{i+1}" if i < len(stickers_list)-1 else "vout"
            
            # Determine Position based on 'pos' string or 'x/y' coordinates
            margin = 20
            
            # Default to Bottom-Right
            calc_x = f"W-w-{margin}"
            calc_y = f"H-h-{margin}"
            
            if "Custom" in s_pos or "Tùy chỉnh" in s_pos:
                # Use raw coordinates (0-1 percentage)
                calc_x = f"W*{flt(s_x)}"
                calc_y = f"H*{flt(s_y)}"
            else:
                # Use Preset Logic (Matches UI Preview)
                # Vertical
                if "Top" in s_pos or "trên" in s_pos:
                    calc_y = f"{margin}"
                elif "Bottom" in s_pos or "dưới" in s_pos:
                    calc_y = f"H-h-{margin}"
                elif "Center" in s_pos or "giữa" in s_pos:
                    calc_y = f"(H-h)/2"
                    
                # Horizontal
                if "Left" in s_pos or "trái" in s_pos:
                    calc_x = f"{margin}"
                elif "Right" in s_pos or "phải" in s_pos:
                    calc_x = f"W-w-{margin}"
                elif "Center" in s_pos or "giữa" in s_pos:
                    calc_x = f"(W-w)/2"
            
            x_expr = calc_x
            y_expr = calc_y
            
            # FFmpeg input index for this sticker (starts at 1, since 0 is video)
            sticker_input_idx = i + 1 
            
            # Build overlay filter for this sticker
            # OPTIMIZATION: If we know target_w/h, use simple 'scale' instead of 'scale2ref'
            # This is much more stable and avoids "Invalid Argument" errors
            use_simple_scale = (isinstance(target_w, int) and target_w > 0 and 
                                isinstance(target_h, int) and target_h > 0)
            
            if use_simple_scale:
                # Calculate sticker width in Python (Force Even)
                stk_w_px = int(target_w * float(s_scale))
                if stk_w_px % 2 != 0: stk_w_px += 1
                
                sticker_filter = (
                    f"[{sticker_input_idx}:v]format=yuva420p,scale={stk_w_px}:-2[{stk_label}];"
                    f"[{current_label}][{stk_label}]overlay={x_expr}:{y_expr}:shortest=1[{next_label}]"
                )
            else:
                # Fallback for "Original" mode (unknown resolution)
                # Force Even Dimensions: Width truncated to even, Height auto even (-2)
                sticker_filter = (
                    f"[{sticker_input_idx}:v]format=yuva420p[{stk_label}_alpha];"
                    f"[{stk_label}_alpha][{current_label}]scale2ref=w=trunc(rw*{flt(s_scale)}/2)*2:h=-2[{stk_label}][bg{i}];"
                    f"[bg{i}][{stk_label}]overlay={x_expr}:{y_expr}:shortest=1[{next_label}]"
                )
            
            sticker_filters.append(sticker_filter)
            current_label = next_label
        
        # Combine all sticker filters
        if sticker_filters:
            if vf:
                vf = vf + ";" + ";".join(sticker_filters)
            else:
                vf = ";".join(sticker_filters)
            
            final_output_label = "vout"

    # Append Drawbox and Text Outro (Independent overlays)
    extra_filters = []
    if drawbox_filter: extra_filters.append(drawbox_filter)
    if text_outro_filter: extra_filters.append(text_outro_filter)
    
    if extra_filters:
        extra_chain = ",".join(extra_filters)
        
        if final_output_label == "vout":
            # Start from [vout]
            vf = vf + f";[vout]{extra_chain}[vout_final]"
            final_output_label = "vout_final"
        elif has_complex_filter:
            # Start from [v_main]
            if vf:
                vf = vf + f";[v_main]{extra_chain}[v_final]"
            else:
                vf = f"[v_main]{extra_chain}[v_final]"
            final_output_label = "v_final"
        else:
            # Simple chain
            if vf:
                vf = vf + "," + extra_chain
            else:
                vf = extra_chain

    
    # Append Subtitles LAST (After everything including Sticker and Black Bar)
    if subtitle_cmd:
        if vf:
            # If final_output_label is set, use it as input for subtitles
            if final_output_label:
                vf = f"{vf};[{final_output_label}]{subtitle_cmd}[v_subs]"
                final_output_label = "v_subs"
            else: # No complex chain, just append
                vf = f"{vf},{subtitle_cmd}"
        else:
            vf = subtitle_cmd

    # Audio filters
    audio_filters = []
    
    volume_boost = settings.get('volume_boost', 1.0)
    if volume_boost != 1.0:
        audio_filters.append(f"volume={volume_boost}")
    
    if speed_factor != 1.0:
        audio_filters.append(f"atempo={speed_factor}")
    
    bass_boost = settings.get('bass_boost', 0)
    if bass_boost > 0:
        audio_filters.append(f"bass=g={bass_boost}")
    
    treble_boost = settings.get('treble_boost', 0)
    if treble_boost > 0:
        audio_filters.append(f"treble=g={treble_boost}")
    
    af = ','.join(audio_filters) if audio_filters else None
    
    # Build FFmpeg command
    cmd = [ffmpeg_path, '-y']
    
    if start_time > 0:
        cmd.extend(['-ss', str(start_time)])
    
    # NEW: Enable Hardware Acceleration (OpenGL/CUDA/DXVA2) if GPU enabled
    # This satisfies the "OpenGL" request by enabling GPU-based decoding/filtering where supported
    if use_gpu:
        cmd.extend(['-hwaccel', 'auto'])
    
    cmd.extend(['-i', input_path])
    
    # NEW: Add Multiple Sticker Inputs if enabled
    if enable_sticker and stickers_list:
        for sticker in stickers_list:
            sticker_path = sticker.get('path', '')
            if sticker_path and os.path.exists(sticker_path):
                # Use -stream_loop -1 for infinite looping of sticker (works with GIF/PNG)
                # This prevents shortest=1 from cutting output to 1 frame when using sticker
                cmd.extend(['-stream_loop', '-1', '-i', sticker_path])
        
    if duration:
        cmd.extend(['-t', str(duration)])
    
    if vf:
        # Use -filter_complex to support both simple and complex chains safely
        cmd.extend(['-filter_complex', vf])
        
        # Map the filter output explicitly
        if enable_sticker and stickers_list:
            # Stickers present - output is [vout] or [vout_final] if drawbox
            output_label = final_output_label if final_output_label else "vout"
            cmd.extend(['-map', f'[{output_label}]'])
        elif has_complex_filter:
            # Complex filter (blur background) - output is [v_main] or [v_final] if drawbox
            output_label = final_output_label if final_output_label else "v_main"
            cmd.extend(['-map', f'[{output_label}]'])
        # else: simple filters, FFmpeg auto-maps
    
    if af:
        cmd.extend(['-af', af])
    
    # Codec settings - MAXIMUM SAFE SPEED
    # Add explicit mapping for AUDIO
    cmd.extend(['-map', '0:a?'])
    
    # CLEAR ROTATION METADATA
    # Since we apply scaling/filters that physically rotate/resize the frame, 
    # we must ensure the 'rotate' tag is cleared or else players will rotate it AGAIN.
    if vf or has_complex_filter:
        cmd.extend(['-metadata:s:v:0', 'rotate=0'])
    
    # FORCE DISPLAY ASPECT RATIO (DAR)
    if "9:16" in ratio_str:
        cmd.extend(['-aspect', '9:16'])
    elif "16:9" in ratio_str:
        cmd.extend(['-aspect', '16:9'])
    elif "1:1" in ratio_str:
        cmd.extend(['-aspect', '1:1'])
    elif "4:3" in ratio_str:
        cmd.extend(['-aspect', '4:3'])
    elif "Original" in ratio_str and target_w > 0 and target_h > 0:
        # Force detected original aspect ratio
        cmd.extend(['-aspect', f'{target_w}:{target_h}'])
    
    codec = 'h264_nvenc' if use_gpu else 'libx264'
    
    if use_gpu:
        # GPU encoding - fastest stable preset
        cmd.extend([
            '-c:v', codec,
            '-preset', 'p1',  # p1 = fastest (Ultra performance)
            '-rc', 'vbr',
            '-b:v', '2800k',  # Slightly lower for speed
            '-maxrate', '3500k',
            '-bufsize', '5000k',
            '-r', '30',
            '-g', '60',  # GOP size for faster encoding
        ])
    else:
        # CPU encoding - fastest stable preset
        cmd.extend([
            '-c:v', codec,
            '-preset', 'faster',  # faster (between fast and veryfast)
            '-crf', '24',  # Slightly higher for speed
            '-r', '30',
            '-g', '60',
        ])
    
    
    # Common Audio Standards & Compatibility
    cmd.extend([
        '-pix_fmt', 'yuv420p', # FORCE standard pixel format (Critical for player compatibility)
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', '44100', # Force 44.1kHz
        '-ac', '2',     # Force Stereo
    ])
    
    # OPTIMIZATION: Limit Threads per FFmpeg process
    # Explicitly limiting threads prevents system freeze when multiple videos process in parallel.
    # Logic: Assume user runs ~2-3 parallel conversions.
    # Each FFmpeg should use subset of cores, not ALL cores.
    # For 12 cores -> use 4 threads. For 4 cores -> use 2 threads.
    try:
        cpu_count = multiprocessing.cpu_count()
        # Allocate roughly 1/3 of cores per process, min 2, max 8
        threads_per_proc = max(2, min(8, cpu_count // 3))
        cmd.extend(['-threads', str(threads_per_proc)])
    except:
        cmd.extend(['-threads', '2']) # Safe fallback

    cmd.append(output_path)
    
    # Run FFmpeg with Real-time Progress Monitoring
    log(f"   [DEBUG] Targets: W={target_w}, H={target_h} | Ratio: {ratio_str} | Simple: {simple_mode}")
    log(f"   [DEBUG] Scale Input: W={scale_w}, H={scale_h}")
    # log(f"   [DEBUG] Command: {' '.join(cmd)}")
    log(f"   🎬 Đang xử lý video với FFmpeg... (Mode: {'GPU' if use_gpu else 'CPU'})")
    
    import re
    duration_sec = duration if duration else 0
    
    # Process Priority Management
    # Set to BELOW_NORMAL_PRIORITY_CLASS (0x00004000) so UI stays responsive
    # and mouse/keyboard doesn't lag even at 100% CPU.
    # On non-Windows, we would use nice() via psutil after spawn, but creationflags is better for Windows start.
    creation_flags = 0
    if sys.platform == 'win32':
        creation_flags = subprocess.CREATE_NO_WINDOW | 0x00004000 # BELOW_NORMAL_PRIORITY_CLASS
    
    # Needs explicit path check for Popen on Windows sometimes, but usually fine
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True, # Text mode
        encoding='utf-8',
        errors='ignore',
        creationflags=creation_flags
    )
    
    # Read stderr for progress
    last_log_time = 0
    import time
    
    # Initialize output queue for thread-safe communication
    output_queue = queue.Queue()
    
    def reader_thread(pipe, q):
        try:
            with pipe:
                for line in iter(pipe.readline, ''):
                    q.put(line)
        except ValueError:
            pass # Handle closed file error (e.g. when process is killed)
        finally:
            q.put(None) # Sentinel to mark end
            
    # Start reader thread
    t = threading.Thread(target=reader_thread, args=(process.stderr, output_queue))
    t.daemon = True
    t.start()
    
    # Non-blocking loop
    stopped_by_user = False
    
    while True:
        # Check Stop Signal
        if check_stop_signal and check_stop_signal():
             log("   🛑 Stop received! Killing FFmpeg process...")
             process.kill()
             stopped_by_user = True
             break

        try:
             # Get line from queue with timeout (non-blocking effect)
             line = output_queue.get(timeout=0.1)
        except queue.Empty:
             # Check if process finished
             if process.poll() is not None:
                 break
             continue # Continue loop to check stop signal again

        if line is None: # Sentinel
            break
            
        if line:
            # Try to get Duration if not known
            if duration_sec == 0 and "Duration:" in line:
                try:
                    # Duration: 00:03:00.07, ...
                    dur_str = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)", line)
                    if dur_str:
                        h, m, s = float(dur_str.group(1)), float(dur_str.group(2)), float(dur_str.group(3))
                        duration_sec = h * 3600 + m * 60 + s
                except:
                    pass
            
            # Parse time=00:00:00.00
            if "time=" in line:
                try:
                    time_match = re.search(r"time=(\d{2}):(\d{2}):(\d{2}\.\d+)", line)
                    if time_match and duration_sec > 0:
                        h, m, s = float(time_match.group(1)), float(time_match.group(2)), float(time_match.group(3))
                        current_sec = h * 3600 + m * 60 + s
                        percent = int((current_sec / duration_sec) * 100)
                        
                        # Call progress callback for UI update
                        if progress_callback:
                            progress_callback(percent)
                        
                        # Log every 10% or every 5 seconds to reduce spam
                        now = time.time()
                        if now - last_log_time > 5 or percent % 20 == 0:
                            if now - last_log_time > 2: # Min log interval
                                log(f"      ⏳ Convert: {percent}% ({line.strip().split('time=')[1].split(' ')[0]})")
                                last_log_time = now
                except:
                    pass
                    
            # Also catch specific errors
            if "Error" in line or "Invalid" in line or "failed" in line:
                 # Standard error logging? Maybe too verbose, keep silent unless failed
                 pass

    # Clean shutdown of process
    if stopped_by_user:
        process.wait() # Just wait for it to die, don't try to communicate (avoid I/O error)
        return False
    else:
        stdout, stderr = process.communicate() # Wait for finish
    
    if process.returncode != 0:
        # Check stderr for specific errors
        pass
        
    returncode = process.returncode

    # Fallback/Error Handling Logic
    result_stderr = "" 
    
    # Fallback/Error Handling Logic
    if returncode != 0 and use_gpu:
        # CHECK STOP SIGNAL BEFORE RETRY
        # If user stopped the process, returncode might be non-zero (e.g. 1 or -9)
        # We must NOT retry in that case.
        if check_stop_signal and check_stop_signal():
             log("   🛑 Process stopped by user (GPU). No retry.")
             return False

        # GPU failed
        log("   ⚠️ GPU encoder failed! Retrying with CPU...")
        
        # Recursively call with use_gpu=False via settings
        settings_cpu = settings.copy()
        settings_cpu['use_gpu'] = False
        
        return process_video_with_ffmpeg(
            input_path, output_path, settings_cpu, 
            srt_file=srt_file, log_callback=log_callback, progress_callback=progress_callback,
            check_stop_signal=check_stop_signal
        )
    
    if returncode != 0:
        log(f"   ❌ FFmpeg error: Process returned {returncode}")
        # Note: We consumed stderr earlier, so specific errors are in the log above
        return False
        
    # Check if output file was actually created
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        log(f"   ❌ Output file not created or empty! FFmpeg might have failed silently.")
        return False
        
    log(f"   ✅ Output file created: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

    
    # --- PHASE 2: INTRO / OUTRO CONCATENATION ---
    enable_intro = settings.get('enable_intro', False)
    intro_path = settings.get('intro_path', '')
    enable_outro = settings.get('enable_outro', False)
    outro_path = settings.get('outro_path', '')
    
    has_intro = enable_intro and intro_path and os.path.exists(intro_path)
    has_outro = enable_outro and outro_path and os.path.exists(outro_path)
    
    # Debug logging
    # log(f"   [DEBUG] Enable Intro: {enable_intro}, Path: {intro_path if intro_path else 'None'}")
    # log(f"   [DEBUG] Enable Outro: {enable_outro}, Path: {outro_path if outro_path else 'None'}")
    
    if has_intro or has_outro:
        log("   🔄 Đang xử lý Intro/Outro (Chuẩn hóa & Ghép)...")
        
        # 1. Get Main Video Props to use as Standard
        main_info = None
        
        # Retry mechanism for reading video info
        import time
        for attempt in range(3):
            main_info = get_video_info(output_path)
            if main_info:
                break
            time.sleep(1) # Wait a bit before retry
            
        if not main_info:
            log("   ⚠️ Warning: Không đọc được thông tin video chính.")
            main_info = {'width': 1280, 'height': 720, 'has_audio': True}
            
        target_w = main_info.get('width', 1280)
        target_h = main_info.get('height', 720)
        
        # Ensure dimensions are Even (required for yuv420p)
        if target_w % 2 != 0: target_w -= 1
        if target_h % 2 != 0: target_h -= 1
        
        # Ensure valid dimensions
        if target_w <= 0: target_w = 1280
        if target_h <= 0: target_h = 720
        
        # Temporary files list
        concat_files = []
        temp_files_to_clean = []
        
        # Helper to normalize segment
        import tempfile
        
        def prepare_segment(path, label):
            # Use tempfile to generate unique path
            # delete=False is required on Windows so subprocess can open it
            fd, temp_seg = tempfile.mkstemp(suffix=f"_{label}.mp4")
            os.close(fd) # Close handle so others can access
            
            # Add to cleanup list
            temp_files_to_clean.append(temp_seg)
            
            # Check for audio presence
            info_in = get_video_info(path)
            has_audio_in = info_in.get('has_audio', False) if info_in else False
            
            # log(f"      + Tệp: {os.path.basename(path)} | Audio: {'CÓ' if has_audio_in else 'KHÔNG'} -> Temp: {os.path.basename(temp_seg)}")

            # Determine scaling mode based on settings
            resize_mode = settings.get('resize_mode', 'Fit')
            
            # Special case: If Intro/Outro aspect ratio is wildly different from Main, 
            # blindly 'Fitting' might result in tiny video.
            # But let's respect user choice: "Fill" -> Crop, "Fit" -> Pad.
            
            if "Fill" in resize_mode or "Lấp đầy" in resize_mode:
                # CROP Logic (Fill Screen)
                filters = [
                    f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase",
                    f"crop={target_w}:{target_h}",
                    f"setsar=1",
                    f"fps=30",
                    f"format=yuv420p"
                ]
            else:
                # FIT Logic (Pad with Black)
                filters = [
                    f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease",
                    f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:black",
                    f"setsar=1",
                    f"fps=30",
                    f"format=yuv420p"
                ]
            vf = ','.join(filters)
            
            c = [ffmpeg_path, '-y']
            
            # Timebase setting (Standard 90k)
            # Timebase setting (Standard 90k)
            # c.extend(['-video_track_timescale', '90000']) # REMOVED: Causing "Option not found" error
            
            if not has_audio_in:
                # Inject Silence if missing audio
                # Using anullsrc to generate silent audio matching standard properties
                if use_gpu: c.extend(['-hwaccel', 'auto'])
                c.extend(['-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100', '-i', path])
                # Map Video from [1] (file), Audio from [0] (silence)
                c.extend([
                    '-filter_complex', f"[1:v]{vf}[v]",
                    '-map', '[v]', '-map', '0:a',
                    '-shortest' # Stop when video ends
                ])
            else:
                # Standard conversion
                if use_gpu: c.extend(['-hwaccel', 'auto'])
                c.extend(['-i', path])
                c.extend(['-vf', vf])
                # Force Audio Standard: AAC, 44100Hz, Stereo
                c.extend(['-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '192k'])
            
            # Strict Encoding Params to ensure compatibility between segments
            c.extend([
                '-c:v', 'libx264', 
                '-preset', 'ultrafast', # Speed priority
                '-profile:v', 'high',   # Standard strict profile
                '-level', '4.1', 
                '-r', '30',             # Force 30 fps output container
                '-g', '60',             # GOP size 60 (2s keyframes)
                temp_seg
            ])
            
            # Log command for debugging
            # log(f"      + CMD: {' '.join(c)}")
            
            res = subprocess.run(c, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            
            if res.returncode != 0:
                err = res.stderr.decode('utf-8', errors='ignore')[-300:]
                log(f"      ❌ Lỗi chuẩn hóa {label}: {err}")
                return None
            
            return temp_seg

        try:
            # Use lock to prevent race conditions when multiple videos concat simultaneously
            with CONCAT_LOCK:
                # log("   🔒 Acquired concat lock")
                
                # A. Prepare Intro
                if has_intro:
                    log("   🔹 Chuẩn hóa Intro...")
                    intro_seg = prepare_segment(intro_path, "intro")
                    if intro_seg:
                        concat_files.append(intro_seg)
                    else:
                        log("   ⚠️ Intro preparation failed.")
                
                # B. Prepare Main Video
                # CRITICAL: We MUST Normalize the main video too, even if we just made it.
                # Why? Because 'Concat Demuxer' fails if there are tiny differences in SAR/Timebase.
                # Re-encoding 'main_temp' ensures it matches 'intro'/'outro' perfectly.
                log("   🔹 Chuẩn hóa Video Chính (Re-encoding for perfect concat)...")
                main_seg = prepare_segment(output_path, "main_temp")
                
                if main_seg:
                    concat_files.append(main_seg)
                else:
                    log("   ❌ Lỗi chuẩn hóa video chính! Dừng ghép.")
                    return True # Keep original
                
                # C. Prepare Outro
                if has_outro:
                    log("   🔹 Chuẩn hóa Outro...")
                    outro_seg = prepare_segment(outro_path, "outro")
                    if outro_seg:
                        concat_files.append(outro_seg)
                    else:
                        log("   ⚠️ Outro preparation failed.")
                
                # Check if we have anything to concat
                if len(concat_files) <= 1:
                    log("   ⚠️ Không đủ video để ghép (chỉ có 1 phần).")
                    return True

                
                # D. Concat using Concat Demuxer
                log(f"   🔗 Đang ghép nối {len(concat_files)} phần...")
                
                # Create temp list file
                fd, list_path = tempfile.mkstemp(suffix="_concat_list.txt", text=True)
                os.close(fd)
                temp_files_to_clean.append(list_path)

                # BACKUP ORIGINAL MAIN VIDEO
                # Before we overwrite output_path with concat result, we must backup
                # because main_seg is a RE-ENCODED version (lower quality/ultrafast).
                # If concat fails, we want the ORIGINAL high-quality video back.
                backup_path = output_path + ".original_backup.mp4"
                try:
                    shutil.copy2(output_path, backup_path)
                    temp_files_to_clean.append(backup_path) # Ensure cleanup
                except Exception as e:
                    log(f"   ⚠️ Warning: Could not backup original video: {e}")
                    backup_path = None
                
                with open(list_path, "w", encoding='utf-8') as f:
                    for vid in concat_files:
                        abs_path = os.path.abspath(vid)
                        safe_path = abs_path.replace('\\', '/').replace("'", "'\\''")
                        f.write(f"file '{safe_path}'\n")
                
                cmd_concat = [
                    ffmpeg_path, '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', list_path,
                    '-c', 'copy', # COPY STREAM (Fast)
                    output_path
                ]
                
                # Run
                res = subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
                
                if res.returncode == 0:
                    log("   ✅ Ghép Intro/Outro thành công (Smart Copy)!")
                else:
                    log(f"   ❌ Lỗi ghép: {res.stderr.decode()[-300:]}")
                    # RESTORE FROM BACKUP
                    if backup_path and os.path.exists(backup_path):
                         log("   ↺ Đang khôi phục video gốc (chất lượng cao)...")
                         shutil.copy2(backup_path, output_path)
                    elif main_seg and os.path.exists(main_seg):
                         # Fallback to re-encoded version if backup failed
                         log("   ↺ Đang khôi phục video (phiên bản re-encode)...")
                         shutil.copy2(main_seg, output_path)
                
                # log("   🔓 Released concat lock")

        except Exception as e:
            log(f"   ❌ Exception during concat: {e}")
            import traceback
            traceback.print_exc()
            
        # Cleanup
        for f in temp_files_to_clean:
            if os.path.exists(f): 
                try: os.remove(f)
                except: pass
                
    return True




def get_video_info(video_path):
    """Get video information using ffmpeg -i (fallback if ffprobe missing)"""
    import re
    import shutil
    
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
    except:
        ffmpeg_path = 'ffmpeg'
        
    # FFmpeg prints info to stderr
    # Check connectivity
    if ffmpeg_path != 'ffmpeg' and not os.path.exists(ffmpeg_path):
        print(f"CRITICAL: FFmpeg binary not found at {ffmpeg_path}")
        ffmpeg_path = 'ffmpeg' # Fallback to system path
        
    if ffmpeg_path == 'ffmpeg' and not shutil.which('ffmpeg'):
         print(f"CRITICAL: 'ffmpeg' command not found in SYSTEM PATH. Please install FFmpeg or check PATH.")
        
    print(f"DEBUG: Using FFmpeg at: {ffmpeg_path}")
    
    cmd = [ffmpeg_path, '-hide_banner', '-i', video_path]
    
    try:
        # We expect a non-zero return code because we didn't specify output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        output = result.stderr
        
        info = {'has_audio': False, 'width': 1280, 'height': 720, 'duration': 0} # Default/Fallback
        
        # Regex to find Duration
        duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', output)
        if duration_match:
            hours = int(duration_match.group(1))
            minutes = int(duration_match.group(2))
            seconds = float(duration_match.group(3))
            info['duration'] = hours * 3600 + minutes * 60 + seconds
        
        # Regex to find Video Stream resolution
        # Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 720x1280 [SAR 1:1 DAR 9:16], ...
        # Standard: 720x1280
        # With spaces: 720 x 1280
        video_match = re.search(r'Video:.*?, (\d+)x(\d+)', output)
        if video_match:
            w = int(video_match.group(1))
            h = int(video_match.group(2))
            
            # Check for Rotation in metadata (displaymatrix: rotation of -90.00 degrees)
            # This is common in phone videos
            rotate_match = re.search(r'rotation of ([-+]?\d+\.\d+) degrees', output)
            if rotate_match:
                rotation = float(rotate_match.group(1))
                if abs(rotation) == 90 or abs(rotation) == 270:
                    print(f"DEBUG: Detected rotation {rotation} deg. Swapping {w}x{h} -> {h}x{w}")
                    w, h = h, w
            
            info['width'] = w
            info['height'] = h
            
        # Regex to find Audio Stream
        if re.search(r'Stream #.*?: Audio:', output):
            info['has_audio'] = True
            
        return info

    except Exception as e:
        print(f"Error getting video info: {e}")
        return None


def normalize_segment_for_concat(input_path, aspect_ratio, label, log_callback=None, use_gpu=True):
    """
    Pre-normalize intro/outro segment for concat (called once, shared by all videos)
    
    Args:
        input_path: Path to intro/outro video
        aspect_ratio: Target aspect ratio (e.g., "9:16 (TikTok/Shorts)")
        label: Label for temp file (e.g., "intro_shared", "outro_shared")
        log_callback: Optional logging function
        
    Returns:
        Path to normalized segment, or None if failed
    """
    import os
    import sys
    import subprocess
    import tempfile
    
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    # Get FFmpeg path
    ffmpeg_path = "ffmpeg"
    local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg.exe")
    bin_ffmpeg = os.path.join(os.getcwd(), "bin", "ffmpeg.exe")
    
    if os.path.exists(local_ffmpeg):
        ffmpeg_path = local_ffmpeg
    elif os.path.exists(bin_ffmpeg):
        ffmpeg_path = bin_ffmpeg
    else:
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            ffmpeg_path = get_ffmpeg_exe()
        except:
            pass
    
    if getattr(sys, 'frozen', False):
        bundled_ffmpeg = os.path.join(sys._MEIPASS, "ffmpeg.exe")
        if os.path.exists(bundled_ffmpeg):
            ffmpeg_path = bundled_ffmpeg
    
    # Parse aspect ratio
    if "9:16" in aspect_ratio:
        w, h = 1080, 1920
    elif "16:9" in aspect_ratio:
        w, h = 1920, 1080
    elif "1:1" in aspect_ratio:
        w, h = 1080, 1080
    elif "4:5" in aspect_ratio:
        w, h = 1080, 1350
    else:
        w, h = 1080, 1920  # Default
    
    # Create temp file
    temp_seg = tempfile.NamedTemporaryFile(suffix=f"_{label}.mp4", delete=False).name
    
    try:
        # Normalize command
        cmd = [
            ffmpeg_path, '-y'
        ]
        
        # Apply GPU accel for intro/outro inputs too
        if use_gpu:
            cmd.extend(['-hwaccel', 'auto'])
            
        cmd.extend(['-i', input_path])
        
        cmd.extend([
            '-vf', f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
            '-r', '30', '-g', '60',
            temp_seg
        ])
        
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                           creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        
        if res.returncode != 0:
            err = res.stderr.decode('utf-8', errors='ignore')[-300:]
            log(f"      ❌ Lỗi normalize {label}: {err}")
            return None
        
        return temp_seg
        
    except Exception as e:
        log(f"      ❌ Exception normalizing {label}: {e}")
        return None

