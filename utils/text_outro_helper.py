"""
Helper function to add text outro to processed video
"""

import os
import subprocess
import tempfile


def add_text_outro_to_video(
    input_video_path,
    output_video_path,
    settings,
    log_callback=None
):
    """
    Add text outro to the end of a video
    
    Args:
        input_video_path: Path to processed video
        output_video_path: Where to save final video
        settings: Dict with text outro settings
        log_callback: Optional logging function
    
    Returns:
        bool: True if successful, False otherwise
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)
    
    try:
        # Check if text outro is enabled
        if not settings.get('enable_outro_text'):
            return False
        
        text_content = settings.get('outro_text_content', '').strip()
        if not text_content:
            log("   ⚠️ Text outro enabled but no content provided")
            return False
            
        style = settings.get('outro_text_style', 'append')
        
        if style == 'overlay':
            return add_overlay_text_outro(input_video_path, output_video_path, settings, log)
        else:
            return add_append_text_outro(input_video_path, output_video_path, settings, text_content, log)

    except Exception as e:
        log(f"   ❌ Error adding text outro: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_append_text_outro(input_video_path, output_video_path, settings, text_content, log):
    """Original logic: Create black video + Concat"""
    log("   📝 Creating text outro (Append mode)...")
    
    from utils.text_outro_generator import create_text_outro_video
    
    # Create text outro video
    text_outro_path = os.path.join(
        tempfile.gettempdir(),
        f"text_outro_{os.path.basename(input_video_path)}"
    )
    
    # Get video dimensions
    width = 1080
    height = 1920
    
    result = create_text_outro_video(
        text=text_content,
        duration=settings.get('outro_text_duration', 5),
        output_path=text_outro_path,
        width=width,
        height=height,
        font_size=settings.get('outro_text_font_size', 60),
        font_color=settings.get('outro_text_font_color', 'white'),
        bg_color=settings.get('outro_text_bg_color', 'black'),
        position=settings.get('outro_text_position', 'center'),
        animation=settings.get('outro_text_animation', 'fade'),
        log_callback=log
    )
    
    if not result or not os.path.exists(text_outro_path):
        log("   ❌ Failed to create text outro")
        return False
    
    log("   🔗 Concatenating text outro to video...")
    
    # Create concat list file
    concat_list = os.path.join(
        tempfile.gettempdir(),
        f"concat_list_{os.path.basename(input_video_path)}.txt"
    )
    
    with open(concat_list, 'w', encoding='utf-8') as f:
        # Use absolute paths and escape backslashes
        main_path = os.path.abspath(input_video_path).replace('\\', '/')
        outro_path = os.path.abspath(text_outro_path).replace('\\', '/')
        f.write(f"file '{main_path}'\n")
        f.write(f"file '{outro_path}'\n")
    
    # Concat videos
    concat_cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_list,
        '-c', 'copy',
        '-y',
        output_video_path
    ]
    
    result = subprocess.run(
        concat_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    
    success = (result.returncode == 0 and os.path.exists(output_video_path))
    
    # Cleanup temp files
    try:
        if os.path.exists(text_outro_path): os.remove(text_outro_path)
        if os.path.exists(concat_list): os.remove(concat_list)
    except: pass
    
    return success


def add_overlay_text_outro(input_video_path, output_video_path, settings, log):
    """New logic: Overlay text on the last N seconds of the video"""
    log("   📝 Applying text outro (Overlay mode)...")
    
    text = settings.get('outro_text_content', '').strip()
    duration = settings.get('outro_text_duration', 5)
    font_size = settings.get('outro_text_font_size', 60)
    font_color = settings.get('outro_text_font_color', 'white')
    position = settings.get('outro_text_position', 'center')
    
    # Escape text
    safe_text = text.replace("'", "'\\\\\\''").replace(":", "\\:")
    
    # Get video duration first to calculate start time
    try:
        probe_cmd = [
            'ffprobe', '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            input_video_path
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        video_duration = float(result.stdout.strip())
        start_time = max(0, video_duration - duration)
    except:
        log("   ⚠️ Could not probe duration, using default overlay logic")
        start_time = 0 # Fallback (should not happen usually)

    # Position logic
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
    
    # Box/Background logic (NEW)
    box_params = ""
    if settings.get('outro_text_box', False):
        box_bg_color = settings.get('outro_text_bg_color', 'black')
        padding = int(settings.get('outro_text_box_padding', 15))
        
        log(f"   [DEBUG] Overlay Text Box: bg={box_bg_color}, padding={padding}")
        
        if box_bg_color != 'transparent':
            # FFmpeg drawtext box syntax
            if '@' not in box_bg_color:
                box_params = f"box=1:boxcolor={box_bg_color}@0.7:boxborderw={padding}:"
            else:
                box_params = f"box=1:boxcolor={box_bg_color}:boxborderw={padding}:"
    
    # Build Drawtext Filter with Box support
    # Box params MUST come first
    drawtext = (
        f"drawtext={box_params}text='{safe_text}':"
        f"fontfile=/Windows/Fonts/arial.ttf:"
        f"fontsize={font_size}:"
        f"fontcolor={font_color}:"
        f"x={x_pos}:y={y_pos}:"
        f"enable='between(t,{start_time},{video_duration})'"
    )

    
    # FFmpeg Command (Re-encode required for filter)
    cmd = [
        'ffmpeg',
        '-i', input_video_path,
        '-vf', drawtext,
        '-c:a', 'copy',
        '-c:v', 'libx264', # Re-encode video
        '-preset', 'fast',
        '-y',
        output_video_path
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    
    if result.returncode == 0 and os.path.exists(output_video_path):
        log("   ✅ Overlay Text Outro applied!")
        return True
    else:
        error = result.stderr.decode('utf-8', errors='ignore')
        log(f"   ❌ Overlay failed: {error[:200]}")
        return False



# Test function
if __name__ == "__main__":
    # Test adding text outro to a video
    test_settings = {
        'enable_outro_text': True,
        'outro_text_content': 'Thanks for watching!\nSubscribe for more!',
        'outro_text_duration': 5,
        'outro_text_font_size': 80,
        'outro_text_font_color': 'white',
        'outro_text_bg_color': 'black',
        'outro_text_position': 'center',
        'outro_text_animation': 'fade'
    }
    
    # You need a test video file
    input_video = "test_input.mp4"
    output_video = "test_output_with_outro.mp4"
    
    if os.path.exists(input_video):
        result = add_text_outro_to_video(
            input_video,
            output_video,
            test_settings
        )
        
        if result:
            print(f"✅ Test successful: {output_video}")
        else:
            print("❌ Test failed")
    else:
        print(f"❌ Test video not found: {input_video}")
