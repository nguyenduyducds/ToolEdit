"""Tool to diagnose outro file issues"""

import sys
import os
import subprocess

def check_video_file(file_path):
    """Check if video file is valid and get info"""
    print(f"\n{'='*60}")
    print(f"Checking: {os.path.basename(file_path)}")
    print(f"{'='*60}\n")
    
    # 1. Check file exists
    if not os.path.exists(file_path):
        print("❌ File does not exist!")
        return False
    
    print(f"✅ File exists")
    print(f"   Size: {os.path.getsize(file_path) / (1024*1024):.2f} MB\n")
    
    # 2. Try to get video info with FFmpeg
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
    except:
        ffmpeg_path = 'ffmpeg'
    
    cmd = [ffmpeg_path, '-hide_banner', '-i', file_path]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        output = result.stderr
        
        # Parse info
        print("📊 Video Info:")
        
        # Find video stream
        import re
        video_match = re.search(r'Stream #.*?: Video: (.*?), (.*?), (\d+)x(\d+)', output)
        if video_match:
            codec = video_match.group(1)
            pixel_fmt = video_match.group(2)
            width = video_match.group(3)
            height = video_match.group(4)
            print(f"   Video: {codec}")
            print(f"   Format: {pixel_fmt}")
            print(f"   Resolution: {width}x{height}")
        else:
            print("   ❌ No video stream found!")
            return False
        
        # Find audio stream
        audio_match = re.search(r'Stream #.*?: Audio: (.*?), (\d+) Hz', output)
        if audio_match:
            audio_codec = audio_match.group(1)
            sample_rate = audio_match.group(2)
            print(f"   Audio: {audio_codec}")
            print(f"   Sample Rate: {sample_rate} Hz")
        else:
            print("   ⚠️ No audio stream (will inject silence)")
        
        # Find duration
        duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', output)
        if duration_match:
            h, m, s = duration_match.groups()
            print(f"   Duration: {h}:{m}:{s}")
        
        # Check for errors
        if 'Invalid data' in output or 'corrupt' in output.lower():
            print("\n❌ File appears to be CORRUPT!")
            print(f"   Error: {output[-500:]}")
            return False
        
        print("\n✅ File appears to be VALID")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg timeout - file may be corrupt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_normalize(file_path):
    """Test if file can be normalized (like prepare_segment does)"""
    print(f"\n{'='*60}")
    print("Testing Normalization (720x1280)")
    print(f"{'='*60}\n")
    
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
    except:
        ffmpeg_path = 'ffmpeg'
    
    output_test = "test_normalized.mp4"
    
    # Simulate prepare_segment logic
    vf = "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1"
    
    cmd = [
        ffmpeg_path, '-y',
        '-i', file_path,
        '-vf', vf,
        '-c:a', 'aac', '-ar', '44100', '-ac', '2',
        '-r', '30',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-b:v', '6000k',
        '-t', '5',  # Only 5 seconds for test
        output_test
    ]
    
    print("Running normalization test (5 seconds)...")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        if result.returncode == 0:
            print("✅ Normalization SUCCESSFUL!")
            print(f"   Output: {output_test}")
            
            # Clean up
            if os.path.exists(output_test):
                size = os.path.getsize(output_test) / (1024*1024)
                print(f"   Size: {size:.2f} MB")
                os.remove(output_test)
            
            return True
        else:
            error = result.stderr.decode('utf-8', errors='ignore')
            print("❌ Normalization FAILED!")
            print(f"   Error: {error[-500:]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Normalization timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    # Test the outro file
    outro_path = r"D:/EditVideo/outtro/0106 (2)(1).mp4"
    
    print("\n🔍 OUTRO FILE DIAGNOSTIC TOOL")
    print("="*60)
    
    # Check file
    is_valid = check_video_file(outro_path)
    
    if is_valid:
        # Test normalization
        can_normalize = test_normalize(outro_path)
        
        if can_normalize:
            print("\n" + "="*60)
            print("✅ CONCLUSION: File is VALID and can be used!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ CONCLUSION: File is valid but CANNOT be normalized!")
            print("   Recommendation: Re-encode the file or use a different outro")
            print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ CONCLUSION: File is INVALID or CORRUPT!")
        print("   Recommendation: Use a different outro file")
        print("="*60)
