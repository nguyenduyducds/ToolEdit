"""Helper utility functions"""

import os
import threading


# GPU Encoding Limiter - Prevent NVENC overload
GPU_ENCODE_SEMAPHORE = threading.Semaphore(10)



def detect_optimal_threads():
    """
    🚀 AUTO-DETECT optimal thread count based on system specs
    Returns: int (1-10)
    """
    try:
        import psutil
        
        # Get system info
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        available_ram_gb = psutil.virtual_memory().available / (1024**3)
        cpu_cores = psutil.cpu_count(logical=False) or 2  # Physical cores
        
        # Check GPU (NVIDIA NVENC)
        has_gpu = False
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            has_gpu = result.returncode == 0
        except:
            pass
        
        # Calculate optimal threads
        # Rule 1: RAM-based (each video + Whisper needs ~2GB)
        ram_threads = max(1, int(available_ram_gb / 2))
        
        # Rule 2: CPU-based (leave half for system)
        cpu_threads = max(1, cpu_cores // 2)
        
        # Rule 3: GPU bonus
        gpu_bonus = 3 if has_gpu else 0
        
        # Final decision: MIN of constraints, MAX 10
        optimal = min(ram_threads, cpu_threads + gpu_bonus, 10)
        optimal = max(1, optimal)  # At least 1
        
        print(f"🔍 System Specs: RAM={total_ram_gb:.1f}GB (Available={available_ram_gb:.1f}GB), CPU={cpu_cores} cores, GPU={'YES' if has_gpu else 'NO'}")
        print(f"🚀 Optimal Threads: {optimal} (RAM limit={ram_threads}, CPU limit={cpu_threads}, GPU bonus={gpu_bonus})")
        
        return optimal
    except Exception as e:
        print(f"⚠️ Auto-detect failed: {e}. Using default 2 threads.")
        return 2


def get_video_files(directory):
    """Get all video files from a directory
    
    Args:
        directory (str): Directory path to scan
        
    Returns:
        list: List of video filenames
    """
    from config.settings import VIDEO_EXTENSIONS
    
    if not os.path.exists(directory):
        return []
    
    video_files = []
    for file in os.listdir(directory):
        if file.lower().endswith(VIDEO_EXTENSIONS):
            video_files.append(file)
    
    return sorted(video_files)
