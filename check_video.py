"""Check video file validity"""

import os
import sys
import subprocess

def check_video_file(video_path):
    """Check if video file is valid and playable"""
    
    print(f"\n{'='*60}")
    print(f"Checking: {os.path.basename(video_path)}")
    print(f"{'='*60}\n")
    
    # 1. Check file exists
    if not os.path.exists(video_path):
        print("❌ File does not exist!")
        return False
    
    # 2. Check file size
    size = os.path.getsize(video_path)
    size_mb = size / (1024 * 1024)
    
    print(f"File Size: {size_mb:.2f} MB")
    
    if size == 0:
        print("❌ File is EMPTY (0 bytes)!")
        return False
    elif size < 1024:
        print("⚠️ File is very small (< 1KB) - likely corrupt!")
        return False
    
    # 3. Check with FFprobe
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
        ffprobe_path = ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe').replace('ffmpeg-win-x86_64-v7.1.exe', 'ffprobe-win-x86_64-v7.1.exe')
    except:
        ffprobe_path = 'ffprobe'
    
    cmd = [
        ffprobe_path,
        '-v', 'error',
        '-show_entries', 'stream=codec_type,codec_name,width,height,duration',
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
        
        if result.returncode != 0:
            print(f"❌ FFprobe error: {result.stderr}")
            return False
        
        output = result.stdout
        print("Stream Info:")
        print(output)
        
        # Parse
        has_video = 'codec_type=video' in output
        has_audio = 'codec_type=audio' in output
        
        if not has_video:
            print("\n❌ No video stream found!")
            return False
        
        if not has_audio:
            print("\n⚠️ No audio stream (video only)")
        
        # Check duration
        if 'duration=' in output:
            duration_line = [l for l in output.split('\n') if 'duration=' in l]
            if duration_line:
                duration = duration_line[0].split('=')[1]
                print(f"\nDuration: {duration} seconds")
                
                if float(duration) < 0.1:
                    print("⚠️ Duration is very short!")
        
        print("\n✅ File appears to be VALID")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    # Check output videos
    output_dir = r"D:\EditVideo\Output"
    
    videos = [
        "edited_Entitled Woman Gets Huge Reality Check_part1.mp4",
        "edited_Evil Teens KlLL 20yo Girl Fun_part1.mp4"
    ]
    
    print("\n🔍 VIDEO FILE CHECKER")
    print("="*60)
    
    for video in videos:
        video_path = os.path.join(output_dir, video)
        is_valid = check_video_file(video_path)
        
        if not is_valid:
            print(f"\n⚠️ RECOMMENDATION: Re-render this video!")
        
        print()
    
    print("="*60)
    print("\nIf files are VALID but still can't play:")
    print("1. Try VLC Media Player")
    print("2. Try Windows Media Player")
    print("3. Check codec: Should be H.264 + AAC")
    print("="*60)
