
import os
import sys
import psutil
import multiprocessing

def detect_optimal_threads():
    """
    Detect optimal number of threads based on CPU cores and Available RAM.
    Formula: Min(CPU_Cores - 2, RAM_Available_GB // 2)
    But at least 1, and max 8 (to avoid overloading disk I/O).
    """
    try:
        # 1. CPU Count
        cpu_count = multiprocessing.cpu_count()
        
        # 2. RAM Available (GB)
        try:
            mem = psutil.virtual_memory()
            ram_gb = mem.available / (1024 ** 3)
            ram_limit = int(ram_gb / 1.5)
        except:
            # Fallback if psutil missing or error
            ram_gb = 8.0 # Assume 8GB
            ram_limit = 4
        
        # Logic:
        # Each FFmpeg process takes ~1-1.5 GB RAM when doing complex filters
        # Keep 2-3 GB for OS
        
        # CPU Limit (Save 2 cores for UI/OS)
        cpu_limit = max(1, cpu_count - 2)
        
        # RAM Limit (Safe Estimate: 1.5GB per thread)
        # ram_limit is calculated above in try-except block
        
        # GPU Check (Optional Bonus)
        gpu_bonus = 0
        try:
             # Basic check if NVIDIA GPU is present via nvidia-smi (very rough)
             # Better to trust CPU limit mainly
             pass
        except:
            pass

        # Optimal is min of constraints
        optimal = min(cpu_limit, ram_limit)
        
        # Bounds
        optimal = max(1, optimal)   # At least 1
        optimal = min(6, optimal)   # Cap at 6 to prevent Disk I/O bottleneck
        
        print(f"🔍 System Specs: RAM={ram_gb:.1f}GB (Available={ram_gb:.1f}GB), CPU={cpu_count} cores")
        print(f"🚀 Optimal Threads: {optimal} (RAM limit={ram_limit}, CPU limit={cpu_limit})")
        
        return optimal
        
    except Exception as e:
        print(f"⚠️ Error detecting specs: {e}. Defaulting to 2.")
        return 2
