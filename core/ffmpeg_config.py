"""FFmpeg configuration for MoviePy and Whisper"""

import sys
import os


def get_ffmpeg_path_robust():
    """Find FFmpeg binary in Frozen (EXE) or Dev environment"""
    path = None
    
    # 1. Check PyInstaller Temp Dir (_MEI...)
    if getattr(sys, 'frozen', False):
        try:
            import imageio_ffmpeg
            # In frozen state, imageio_ffmpeg should be bundled
            # Check specifically in the _MEI folder
            base_path = sys._MEIPASS
            # Look for ffmpeg.exe recursively or in specific folders
            potential_paths = [
                os.path.join(base_path, 'ffmpeg.exe'),
                os.path.join(base_path, 'imageio_ffmpeg', 'binaries', 'ffmpeg-win64-v4.2.2.exe'),
            ]
            
            # Use imageio's own detection if possible
            path = imageio_ffmpeg.get_ffmpeg_exe()
            print(f"   ℹ️ imageio detected: {path}")
        except Exception as e:
            print(f"   ⚠️ imageio lookup failed: {e}")

    # 2. Fallback: Use imageio_ffmpeg normally
    if not path or not os.path.exists(path):
        try:
            import imageio_ffmpeg
            path = imageio_ffmpeg.get_ffmpeg_exe()
        except:
            pass

    return path


def configure_ffmpeg():
    """Configure FFmpeg for MoviePy and Whisper"""
    try:
        ffmpeg_exe = get_ffmpeg_path_robust()
        
        if ffmpeg_exe and os.path.exists(ffmpeg_exe):
            # 1. Set environment variable for MoviePy
            os.environ["MOVIEPY_FFMPEG_BINARY"] = ffmpeg_exe
            
            # 2. Add to system PATH for Whisper/Subprocess
            ffmpeg_dir = os.path.dirname(ffmpeg_exe)
            os.environ["PATH"] += os.pathsep + ffmpeg_dir
            
            print(f"✅ FFmpeg configured: {ffmpeg_exe} (Exists: {os.path.exists(ffmpeg_exe)})")
            return True
        else:
            print("❌ Critical: FFmpeg binary NOT found!")
            return False

    except Exception as e:
        print(f"⚠️ FFmpeg config warning: {e}")
        return False


def import_moviepy():
    """Import MoviePy after FFmpeg configuration"""
    try:
        from moviepy.editor import (
            VideoFileClip, concatenate_videoclips, AudioFileClip, 
            TextClip, CompositeVideoClip, ColorClip, ImageClip
        )
        from moviepy.video import fx as vfx
        from moviepy.audio import fx as afx
        
        print("✅ MoviePy imported successfully")
        
        return {
            'VideoFileClip': VideoFileClip,
            'concatenate_videoclips': concatenate_videoclips,
            'AudioFileClip': AudioFileClip,
            'TextClip': TextClip,
            'CompositeVideoClip': CompositeVideoClip,
            'ColorClip': ColorClip,
            'ImageClip': ImageClip,
            'vfx': vfx,
            'afx': afx
        }
    except ImportError as e:
        print(f"❌ Critical: Failed to import MoviePy: {e}")
        print("⚠️ The application may not work correctly without MoviePy")
        return None


def setup_whisper():
    """Setup Whisper for subtitle generation"""
    import threading
    
    try:
        import whisper
        
        # Smart Semaphore: Allow multiple Whisper instances based on RAM
        try:
            import psutil
            available_ram_gb = psutil.virtual_memory().available / (1024**3)
            max_whisper_instances = max(1, int(available_ram_gb / 3))  # 3GB per instance
            max_whisper_instances = min(max_whisper_instances, 4)  # Cap at 4 for safety
            print(f"🎤 Whisper Semaphore: {max_whisper_instances} concurrent instances (RAM: {available_ram_gb:.1f}GB)")
        except:
            max_whisper_instances = 1  # Fallback to single instance
        
        return {
            'available': True,
            'model': None,  # Will be loaded on demand
            'semaphore': threading.Semaphore(max_whisper_instances)
        }
    except ImportError:
        return {
            'available': False,
            'model': None,
            'semaphore': None
        }


def setup_speech_recognition():
    """Setup Google Speech Recognition as fallback"""
    try:
        import speech_recognition as sr
        return {
            'available': True,
            'module': sr
        }
    except ImportError:
        return {
            'available': False,
            'module': None
        }
