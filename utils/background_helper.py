"""
Background Processing Helper
Auto-minimize to tray when processing starts
"""

from config.settings import AUTO_MINIMIZE_ON_PROCESS, NOTIFY_PER_VIDEO, NOTIFY_ON_COMPLETE


def enable_background_processing(gui_instance):
    """
    Decorator/wrapper to enable background processing
    
    Usage:
        # In main_window.py, at start of start_processing():
        enable_background_processing(self)
    """
    # Auto minimize to tray if enabled
    if AUTO_MINIMIZE_ON_PROCESS and gui_instance.tray_icon:
        try:
            # Get number of files to process
            num_files = len(gui_instance.files_to_process) if hasattr(gui_instance, 'files_to_process') else 0
            
            # Show notification
            gui_instance.log(f"🚀 Bắt đầu xử lý {num_files} video...")
            # gui_instance.log("📱 App sẽ chạy ngầm. Click icon System Tray để mở lại.")
            
            # Minimize to tray after a short delay (let user see the message)
            # DISABLE AUTO MINIMIZE - User Request
            # gui_instance.root.after(1500, gui_instance.minimize_to_tray)
            
            # Show tray notification
            gui_instance.root.after(2000, lambda: gui_instance.show_notification(
                "Video Editor Pro",
                f"🚀 Đang xử lý {num_files} videos..."
            ))
        except Exception as e:
            print(f"⚠️ Background processing setup failed: {e}")


def notify_video_complete(gui_instance, video_name, current, total):
    """
    Show notification when a video is processed
    
    Args:
        gui_instance: VideoEditorGUI instance
        video_name: Name of the processed video
        current: Current video number (1-indexed)
        total: Total number of videos
    """
    if NOTIFY_PER_VIDEO:
        try:
            message = f"✅ Đã xử lý: {video_name} ({current}/{total})"
            gui_instance.show_notification("Video Editor Pro", message)
            gui_instance.log(message)
        except:
            pass


def notify_all_complete(gui_instance, total_processed):
    """
    Show notification when all videos are processed
    
    Args:
        gui_instance: VideoEditorGUI instance
        total_processed: Total number of videos processed
    """
    if NOTIFY_ON_COMPLETE:
        try:
            message = f"🎉 Hoàn thành! Đã xử lý {total_processed} videos"
            gui_instance.show_notification("Video Editor Pro - Hoàn thành", message)
            gui_instance.log(message)
            
            # Optional: Play sound (if available)
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except:
                pass
                
        except:
            pass
