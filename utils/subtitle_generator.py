"""Subtitle generation utilities - Pure functions without UI dependencies"""

import os
import sys
import threading


def generate_subtitles_with_whisper(audio_path, language='en', model_size='small', log_callback=None):
    """
    Generate subtitles using Whisper AI
    
    Args:
        audio_path: Path to audio file
        language: Language code ('en', 'vi', etc.)
        model_size: Whisper model size ('tiny', 'small', 'medium', 'large')
        log_callback: Optional callback function for logging
        
    Returns:
        str: Path to generated SRT file, or None if failed
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    acquired_semaphore = False
    try:
        # Limit concurrent Whisper instances
        if not hasattr(generate_subtitles_with_whisper, "semaphore"):
            generate_subtitles_with_whisper.semaphore = threading.Semaphore(1)
        
        generate_subtitles_with_whisper.semaphore.acquire()
        acquired_semaphore = True

        # --- ATTEMPT FASTER-WHISPER (NVIDIA OPTIMIZED) ---
        try:
            from faster_whisper import WhisperModel
            import torch
            
            # Check CUDA
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            
            log(f"   🚀 Initializing Faster-Whisper (CTranslate2) on {device.upper()} [{compute_type}]...")
            
            # Load Model (CTranslate2 is much faster on GPU)
            # cache_dir=None uses default huggingface cache
            model = WhisperModel(model_size, device=device, compute_type=compute_type)
            
            log(f"   🎤 Transcribing audio (Faster-Whisper)...")
            
            segments_gen, info = model.transcribe(
                audio_path, 
                beam_size=5, 
                language=language if language and language != 'auto' else None,
                word_timestamps=True
            )
            
            # Collect segments (generator to list)
            all_segments = []
            total_words = 0
            
            for seg in segments_gen:
                text = seg.text.strip()
                if not text: continue
                
                # Faster-Whisper segment format is slightly different but compatible for basic usage
                # seg.words is available if word_timestamps=True
                
                if seg.words:
                    total_words += len(seg.words)
                    # Use existing logic for word-level chunks if needed
                    # For now, let's keep it simple or map to the same logic
                    # Mapping Faster-Whisper 'Word' object to dict for consistency with below logic?
                    # Actually, let's just use the segment directly for simplicity in this replacement,
                    # OR adapt the chunking logic if strictly needed.
                    # The user wants SPEED. Segment level is usually fine.
                    # But if we want word-level precision for karaoke styles, we need words.
                    
                    # Let's just output segment for now to ensure robustness
                    all_segments.append((seg.start, seg.end, text))
                    log(f"   📝 [{seg.start:.1f}s]: {text[:30]}...")
                else:
                    all_segments.append((seg.start, seg.end, text))
                    log(f"   📝 [{seg.start:.1f}s]: {text[:30]}...")
            
            # Generate SRT
            if all_segments:
                thread_id = threading.get_ident()
                srt_dir = os.path.join(os.getcwd(), "srt_files")
                os.makedirs(srt_dir, exist_ok=True)
                srt_path = os.path.join(srt_dir, f"temp_subs_{thread_id}.srt")
                
                with open(srt_path, 'w', encoding='utf-8') as f:
                    for idx, (start, end, text) in enumerate(all_segments, 1):
                        h = int(start // 3600)
                        m = int((start % 3600) // 60)
                        s = int(start % 60)
                        ms = int((start % 1) * 1000)
                        h2 = int(end // 3600)
                        m2 = int((end % 3600) // 60)
                        s2 = int(end % 60)
                        ms2 = int((end % 1) * 1000)
                        f.write(f"{idx}\n")
                        f.write(f"{h:02d}:{m:02d}:{s:02d},{ms:03d} --> {h2:02d}:{m2:02d}:{s2:02d},{ms2:03d}\n")
                        f.write(f"{text}\n\n")
                
                log(f"   ✅ SRT Created (Faster-Whisper): {len(all_segments)} segments")
                log(f"   🎯 Detected Language: {info.language} (Probability: {info.language_probability:.2f})")
                return srt_path
            
            else:
                log("   ⚠️ No segments generated.")
                return None

        except ImportError:
            log("   ⚠️ 'faster-whisper' library not found. Falling back to standard OpenAI Whisper...")
            log("   💡 Install with: pip install faster-whisper")
            
            # --- FALLBACK TO STANDARD WHISPER (Original Code) ---
            import whisper
            import torch
            
            # Check Device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            if device == "cpu":
                log("   ⚠️ GPU not detected! Running on CPU (Slow).")
                # Optimize CPU usage: Limit PyTorch to 1 thread to prevent UI lag
                torch.set_num_threads(1)
                torch.set_num_interop_threads(1)
                
                # Diagnostic for Python version
                import sys
                if sys.version_info >= (3, 13):
                    log(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} is likely too new for GPU support!")
                    log("   💡 RECOMMEND: Install Python 3.10, 3.11, or 3.12 to enable CUDA/GPU acceleration.")
            else:
                log(f"   🚀 GPU Detected! Running on {torch.cuda.get_device_name(0)}")
            
            # --- MODEL CACHING LOGIC ---
            global _WHISPER_CACHE, _WHISPER_LOCK
            if '_WHISPER_CACHE' not in globals():
                _WHISPER_CACHE = {}
                _WHISPER_LOCK = threading.Lock()
                
            cache_key = f"{model_size}_{device}"
            model = None
            
            # MEMORY CHECK
            try:
                import psutil
                mem = psutil.virtual_memory()
                available_ram_gb = mem.available / (1024**3)
                if available_ram_gb < 2.0 and model_size not in ['tiny', 'base']:
                    log(f"   ⚠️ Low RAM ({available_ram_gb:.1f}GB). Downgrading to 'tiny'.")
                    model_size = 'tiny'
                    cache_key = f"{model_size}_{device}"
            except: pass
            
            with _WHISPER_LOCK:
                if cache_key in _WHISPER_CACHE:
                    log(f"   ⚡ Using cached Whisper model ({model_size})...")
                    model = _WHISPER_CACHE[cache_key]
                else:
                    log(f"   🎤 Loading Whisper model ({model_size}) on {device.upper()}...")
                    is_frozen = getattr(sys, 'frozen', False)
                    if is_frozen:
                         bundle_dir = sys._MEIPASS
                         whisper_models_dir = os.path.join(bundle_dir, 'whisper_models')
                         if os.path.exists(whisper_models_dir):
                             model = whisper.load_model(model_size, device=device, download_root=whisper_models_dir)
                         else:
                             model = whisper.load_model(model_size, device=device)
                    else:
                        model = whisper.load_model(model_size, device=device)
                    _WHISPER_CACHE[cache_key] = model
            
            log(f"   🎤 Transcribing audio (Standard Whisper)...")
            
            # Redirect stdout for tqdm
            original_stdout = sys.stdout
            if sys.stdout is None: sys.stdout = open(os.devnull, 'w')
            
            try:
                transcribe_params = {'verbose': False, 'word_timestamps': True}
                if language: transcribe_params['language'] = language
                try:
                    result = model.transcribe(audio_path, **transcribe_params)
                except:
                    transcribe_params['word_timestamps'] = False
                    result = model.transcribe(audio_path, **transcribe_params)
            finally:
                sys.stdout = original_stdout
            
            # Collect Segments (Standard Logic)
            all_segments = []
            total_words = 0
            for seg in result.get('segments', []):
                text = seg.get('text', '').strip()
                if not text: continue
                # Simple segment logic for fallback
                all_segments.append((seg.get('start', 0), seg.get('end', 0), text))
                log(f"   📝 [{seg.get('start', 0):.1f}s]: {text[:30]}...")

            # Generate SRT
            if all_segments:
                thread_id = threading.get_ident()
                srt_dir = os.path.join(os.getcwd(), "srt_files")
                os.makedirs(srt_dir, exist_ok=True)
                srt_path = os.path.join(srt_dir, f"temp_subs_{thread_id}.srt")
                
                with open(srt_path, 'w', encoding='utf-8') as f:
                    for idx, (start, end, text) in enumerate(all_segments, 1):
                        h = int(start // 3600)
                        m = int((start % 3600) // 60)
                        s = int(start % 60)
                        ms = int((start % 1) * 1000)
                        h2 = int(end // 3600)
                        m2 = int((end % 3600) // 60)
                        s2 = int(end % 60)
                        ms2 = int((end % 1) * 1000)
                        f.write(f"{idx}\n")
                        f.write(f"{h:02d}:{m:02d}:{s:02d},{ms:03d} --> {h2:02d}:{m2:02d}:{s2:02d},{ms2:03d}\n")
                        f.write(f"{text}\n\n")
                
                log(f"   ✅ SRT Created (Standard): {len(all_segments)} segments")
                return srt_path
            else:
                return None

    except Exception as e:
        log(f"   ❌ Whisper error: {e}")
        import traceback
        log(f"   Traceback: {traceback.format_exc()}")
        return None
    finally:
        if 'acquired_semaphore' in locals() and acquired_semaphore:
            generate_subtitles_with_whisper.semaphore.release()


def generate_subtitles_with_google(audio_path, language='en-US', log_callback=None):
    """
    Generate subtitles using Google Speech Recognition
    
    Args:
        audio_path: Path to audio file
        language: Language code ('en-US', 'vi-VN', etc.)
        log_callback: Optional callback function for logging
        
    Returns:
        str: Path to generated SRT file, or None if failed
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        
        log(f"   🎤 Recognizing speech with Google...")
        
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
        
        text = recognizer.recognize_google(audio_data, language=language)
        
        if text:
            thread_id = threading.get_ident()
            srt_dir = os.path.join(os.getcwd(), "srt_files")
            os.makedirs(srt_dir, exist_ok=True)
            
            srt_path = os.path.join(srt_dir, f"temp_subs_{thread_id}.srt")
            
            # Simple SRT with full text
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write("1\n")
                f.write("00:00:00,000 --> 00:00:10,000\n")
                f.write(f"{text}\n\n")
            
            log(f"   ✅ SRT created with Google Speech Recognition")
            return srt_path
        
        return None
        
    except Exception as e:
        log(f"   ❌ Google Speech Recognition error: {e}")
        return None


def extract_audio_from_video(video_path, output_audio_path, log_callback=None):
    """
    Extract audio from video file
    
    Args:
        video_path: Path to video file
        output_audio_path: Path to output audio file
        log_callback: Optional callback function for logging
        
    Returns:
        bool: True if successful, False otherwise
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
    except:
        ffmpeg_path = 'ffmpeg'
    
    import subprocess
    import sys
    
    cmd = [
        ffmpeg_path, '-y',
        '-i', video_path,
        '-vn',  # No video
        '-acodec', 'pcm_s16le',
        '-ar', '16000',  # 16kHz for speech recognition
        '-ac', '1',  # Mono
        output_audio_path
    ]
    
    log(f"   🎵 Extracting audio...")
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )
    
    if result.returncode != 0:
        error_msg = result.stderr.decode('utf-8', errors='ignore')
        log(f"   ❌ Audio extraction error: {error_msg[-500:]}")
        return False
    
    log(f"   ✅ Audio extracted")
    return True
