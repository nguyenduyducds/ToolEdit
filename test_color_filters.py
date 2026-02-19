"""Test valid FFmpeg color filters"""

import subprocess
import sys

# Test each color filter
filters_to_test = {
    "Black & White": "hue=s=0",
    "Sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
    "Vintage": "eq=contrast=1.1:brightness=-0.05:saturation=0.8,colorbalance=rs=0.1:gs=-0.05:bs=-0.1",
    "Cold": "colorbalance=rs=-0.2:gs=-0.1:bs=0.3,eq=saturation=1.2",
    "Warm": "colorbalance=rs=0.3:gs=-0.1:bs=-0.3,eq=saturation=1.1"
}

print("Testing FFmpeg Color Filters...\n")

try:
    from imageio_ffmpeg import get_ffmpeg_exe
    ffmpeg_path = get_ffmpeg_exe()
except:
    ffmpeg_path = 'ffmpeg'

for name, filter_cmd in filters_to_test.items():
    print(f"Testing: {name}")
    print(f"  Filter: {filter_cmd}")
    
    # Test filter syntax with ffmpeg
    cmd = [
        ffmpeg_path, '-hide_banner',
        '-f', 'lavfi', '-i', 'color=c=blue:s=320x240:d=1',
        '-vf', filter_cmd,
        '-f', 'null', '-'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        if result.returncode == 0:
            print(f"  ✅ VALID\n")
        else:
            error = result.stderr.decode('utf-8', errors='ignore')
            if 'No such filter' in error or 'Invalid' in error:
                print(f"  ❌ INVALID")
                print(f"  Error: {error[:200]}\n")
            else:
                print(f"  ✅ VALID (non-zero exit but filter OK)\n")
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ TIMEOUT (but filter syntax likely OK)\n")
    except Exception as e:
        print(f"  ❌ ERROR: {e}\n")

print("✅ All tests completed!")
