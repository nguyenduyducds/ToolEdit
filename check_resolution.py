"""Check video resolution and metadata"""

import sys
import subprocess

def check_video_resolution(video_path):
    """Check actual video resolution using FFprobe"""
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
        ffprobe_path = ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe').replace('ffmpeg-win-x86_64-v7.1.exe', 'ffprobe-win-x86_64-v7.1.exe')
    except:
        ffprobe_path = 'ffprobe'
    
    cmd = [
        ffprobe_path,
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,display_aspect_ratio,rotation',
        '-of', 'default=noprint_wrappers=1',
        video_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        print(f"\n{'='*60}")
        print(f"Video: {video_path}")
        print(f"{'='*60}\n")
        print(result.stdout)
        
        # Parse output
        lines = result.stdout.strip().split('\n')
        info = {}
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                info[key] = value
        
        width = info.get('width', 'N/A')
        height = info.get('height', 'N/A')
        dar = info.get('display_aspect_ratio', 'N/A')
        rotation = info.get('rotation', '0')
        
        print(f"Resolution: {width}x{height}")
        print(f"Display Aspect Ratio: {dar}")
        print(f"Rotation: {rotation}°")
        
        # Check if correct
        if width == '720' and height == '1280':
            print("\n✅ CORRECT: 9:16 (Portrait/Vertical)")
        elif width == '1280' and height == '720':
            print("\n❌ WRONG: 16:9 (Landscape/Horizontal)")
            print("   Expected: 720x1280 (9:16)")
        else:
            print(f"\n⚠️ UNEXPECTED: {width}x{height}")
        
        return info
        
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    # Check the output video
    video_path = r"D:\EditVideo\Output\edited_Entitled Woman Gets Huge Reality Check_part1.mp4"
    
    print("\n🔍 VIDEO RESOLUTION CHECKER")
    check_video_resolution(video_path)
    
    print("\n" + "="*60)
    print("If resolution is WRONG, the issue is in FFmpeg command!")
    print("="*60)
