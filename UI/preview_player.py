# Video Preview Player Logic
# Handles video playback, pause, seek, and realtime effects

import cv2
import numpy as np
import time
import threading
import gc
from PIL import Image


class VideoPreviewPlayer:
    """Manages video preview playback with pause/seek support"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.stop_preview = False
        self.is_paused = False
        self.seeking = False
        self.seek_target_frame = 0
        
        self.video_total_frames = 0
        self.video_current_frame = 0
        self.video_fps = 24.0
        
    def play_preview_thread(self, filepath, thread_id):
        """Worker Thread: Reads frames, applies effects, handles pause/seek"""
        try:
            import time
            
            # Start UI Polling from Main Thread context
            self.main_window.root.after(0, self.main_window.start_preview_polling)

            cap = cv2.VideoCapture(filepath)
            
            # Get video info
            self.video_total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
            
            # Target 24 FPS (Cinematic/Smooth) - Safe limit
            target_fps = 24.0
            frame_interval = 1.0 / target_fps
            
            frame_count = 0
            
            while not self.stop_preview and cap.isOpened():
                start_time = time.time()
                
                if self.main_window.preview_id != thread_id:
                    break

                # Handle Pause
                while self.is_paused and not self.stop_preview:
                    time.sleep(0.1)
                    if self.main_window.preview_id != thread_id:
                        break
                
                # Handle Seek
                if self.seeking:
                    try:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_target_frame)
                        frame_count = self.seek_target_frame
                        self.seeking = False
                    except:
                        self.seeking = False

                # Loop video
                try:
                    if cap.get(cv2.CAP_PROP_POS_FRAMES) >= cap.get(cv2.CAP_PROP_FRAME_COUNT):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

                    ret, frame = cap.read()
                    if not ret:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        time.sleep(0.1)
                        continue
                except:
                    break
                
                frame_count += 1
                
                # Update seek bar and time display
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                self.video_current_frame = current_frame
                if self.video_total_frames > 0:
                    seek_percent = (current_frame / self.video_total_frames) * 100
                    self.main_window.root.after(0, lambda p=seek_percent: self.main_window.seek_var.set(p))
                    
                    current_time = current_frame / self.video_fps if self.video_fps > 0 else 0
                    total_time = self.video_total_frames / self.video_fps if self.video_fps > 0 else 0
                    time_text = f"{self.format_time(current_time)} / {self.format_time(total_time)}"
                    self.main_window.root.after(0, lambda t=time_text: self.main_window.time_label.config(text=t))
                
                # Apply Speed Preview
                speed_factor = self.main_window.speed_factor.get() if self.main_window.enable_speed.get() else 1.0
                
                if speed_factor > 1.0:
                    skip_frames = int(speed_factor) - 1
                    if skip_frames > 0 and frame_count % (skip_frames + 1) != 0:
                        continue
                
                adjusted_interval = frame_interval / speed_factor
                
                if frame_count % 50 == 0:
                    gc.collect()
                
                # Process frame (resize, apply effects, etc.)
                final_frame = self.process_frame(frame)
                
                # Share with main thread
                self.main_window.latest_frame = final_frame
                
                # Sleep with adjusted interval
                elapsed = time.time() - start_time
                wait = adjusted_interval - elapsed
                if wait < 0.01: wait = 0.01
                time.sleep(wait)
            
        except Exception as e:
            print(f"Preview error: {e}")
        finally:
            # CRITICAL: Always release video capture to prevent file locks
            try:
                if 'cap' in locals() and cap is not None:
                    cap.release()
            except:
                pass
            self.main_window.latest_frame = None
    
    def process_frame(self, frame):
        """Apply all realtime effects to frame"""
        # This will call the effects processor
        from UI.effects_preview import apply_realtime_effects
        return apply_realtime_effects(self.main_window, frame)
    
    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
