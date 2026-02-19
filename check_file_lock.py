"""
Tool to check which process is locking a file
"""
import os
import sys

def check_file_lock(filepath):
    """Check if file is locked and try to identify the process"""
    
    # Method 1: Try to open file exclusively
    try:
        # Try to open with exclusive access
        with open(filepath, 'r+b') as f:
            print(f"✅ File is NOT locked: {filepath}")
            return False
    except PermissionError:
        print(f"❌ File IS locked: {filepath}")
        print(f"   Error: Permission denied (file is open in another process)")
        return True
    except FileNotFoundError:
        print(f"⚠️ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error checking file: {e}")
        return True

if __name__ == "__main__":
    # Check the problematic files
    files = [
        r"input/#animal #help #save #love #foryou #pet #cool #fyp #amazing.mp4",
        r"input/#animal #help #save #love #foryou #pet #cool #fyp #animallove.mp4",
        r"input/#animal #help #save #love #foryou #pet #cool #fyp #cat.mp4"
    ]
    
    print("=" * 60)
    print("FILE LOCK CHECKER")
    print("=" * 60)
    
    for f in files:
        if os.path.exists(f):
            check_file_lock(f)
            print()
        else:
            print(f"⚠️ File not found: {f}\n")
    
    print("=" * 60)
    print("\n💡 GIẢI PHÁP:")
    print("1. Đóng Windows Explorer")
    print("2. Tắt Windows Search Indexing cho folder này")
    print("3. Tắt antivirus tạm thời")
    print("4. Restart máy")
    print("5. Hoặc dùng tool 'Unlocker' để force unlock")
