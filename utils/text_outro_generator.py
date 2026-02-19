"""
Text Outro Generator - Create customizable text outro videos
"""

import subprocess
import os
from pathlib import Path


def create_text_outro_video(
    text,
    duration,
    output_path,
    width=1080,
    height=1920,
    font_size=60,
    font_color="white",
    bg_color="black",
    position="center",
    animation="none",
    font_family="Arial",
    log_callback=None
):
    """
    Create a video with customizable text overlay
    
    Args:
        text: Text to display
        duration: Duration in seconds
        output_path: Where to save the video
        width: Video width (default 1080 for 9:16)
        height: Video height (default 1920 for 9:16)
        font_size: Font size in pixels
        font_color: Text color (name or hex)
        bg_color: Background color (name, hex, or 'gradient')
        position: Text position ('center', 'top', 'bottom')
        animation: Animation type ('none', 'fade', 'slide_up', 'slide_down')
        font_family: Font family name
        log_callback: Optional logging function
    
    Returns:
        str: Path to created video, or None if failed
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)
    
    try:
        log(f"📝 Creating text outro: '{text[:30]}...'")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        # Build FFmpeg filter
        filters = []
        
        # 1. Background
        if bg_color == "gradient":
            # Gradient background (top to bottom)
            bg_filter = f"color=c=#1a1a1a:s={width}x{height}:d={duration}[bg1];" \
                       f"color=c=#000000:s={width}x{height}:d={duration}[bg2];" \
                       f"[bg1][bg2]blend=all_mode=overlay:all_opacity=0.5[bg]"
        else:
            # Solid color background
            bg_filter = f"color=c={bg_color}:s={width}x{height}:d={duration}[bg]"
        
        filters.append(bg_filter)
        
        # 2. Text position
        if position == "center":
            x_pos = "(w-text_w)/2"
            y_pos = "(h-text_h)/2"
        elif position == "top":
            x_pos = "(w-text_w)/2"
            y_pos = "h*0.2"
        elif position == "bottom":
            x_pos = "(w-text_w)/2"
            y_pos = "h*0.8-text_h"
        else:
            x_pos = "(w-text_w)/2"
            y_pos = "(h-text_h)/2"
        
        # 3. Text with optional animation
        # Escape special characters in text
        safe_text = text.replace("'", "'\\\\\\''").replace(":", "\\:")
        
        if animation == "fade":
            # Fade in first 1s, fade out last 1s
            fade_duration = min(1.0, duration / 3)
            text_filter = f"drawtext=text='{safe_text}':" \
                         f"fontfile=/Windows/Fonts/arial.ttf:" \
                         f"fontsize={font_size}:" \
                         f"fontcolor={font_color}:" \
                         f"x={x_pos}:y={y_pos}:" \
                         f"alpha='if(lt(t,{fade_duration}),t/{fade_duration},if(gt(t,{duration-fade_duration}),({duration}-t)/{fade_duration},1))'"
        
        elif animation == "slide_up":
            # Slide up from bottom
            text_filter = f"drawtext=text='{safe_text}':" \
                         f"fontfile=/Windows/Fonts/arial.ttf:" \
                         f"fontsize={font_size}:" \
                         f"fontcolor={font_color}:" \
                         f"x={x_pos}:" \
                         f"y='h-((h-{y_pos})*min(t/{duration},1))'"
        
        elif animation == "slide_down":
            # Slide down from top
            text_filter = f"drawtext=text='{safe_text}':" \
                         f"fontfile=/Windows/Fonts/arial.ttf:" \
                         f"fontsize={font_size}:" \
                         f"fontcolor={font_color}:" \
                         f"x={x_pos}:" \
                         f"y='{y_pos}*min(t/{duration},1)'"
        
        else:  # no animation
            text_filter = f"drawtext=text='{safe_text}':" \
                         f"fontfile=/Windows/Fonts/arial.ttf:" \
                         f"fontsize={font_size}:" \
                         f"fontcolor={font_color}:" \
                         f"x={x_pos}:y={y_pos}"
        
        # Combine filters
        full_filter = f"{';'.join(filters)};[bg]{text_filter}"
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', full_filter,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            '-y',
            output_path
        ]
        
        log(f"   🎬 Running FFmpeg...")
        
        # Run FFmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        if result.returncode == 0 and os.path.exists(output_path):
            log(f"   ✅ Text outro created: {output_path}")
            return output_path
        else:
            error = result.stderr.decode('utf-8', errors='ignore')
            log(f"   ❌ FFmpeg failed: {error[:200]}")
            return None
            
    except Exception as e:
        log(f"   ❌ Error creating text outro: {e}")
        import traceback
        traceback.print_exc()
        return None


# Test function
if __name__ == "__main__":
    # Test creating a text outro
    output = "test_outro.mp4"
    result = create_text_outro_video(
        text="Thanks for watching!\nSubscribe for more!",
        duration=5,
        output_path=output,
        font_size=80,
        font_color="white",
        bg_color="black",
        position="center",
        animation="fade"
    )
    
    if result:
        print(f"✅ Test successful: {result}")
    else:
        print("❌ Test failed")
