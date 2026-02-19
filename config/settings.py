"""Application settings and constants"""

# 📦 APP VERSION INFO
APP_VERSION = "2.0.0"

# Link check update (Gist Raw)
UPDATE_URL = "https://gist.githubusercontent.com/nguyenduyducds/85850359601efe74dbcbe128cca9d7d7/raw"

# Default directories
DEFAULT_INPUT_DIR = "input/"
DEFAULT_OUTPUT_DIR = "output/"
SRT_FILES_DIR = "srt_files"

# Video settings
DEFAULT_START_TIME = 0
DEFAULT_DURATION = 120
DEFAULT_THREADS = 2

# Anti-copyright effects - HARD-CODED OPTIMAL VALUES
DEFAULT_BLUR_AMOUNT = 2.5
DEFAULT_BRIGHTNESS = 1.0
DEFAULT_ZOOM_FACTOR = 1.05
DEFAULT_SPEED_FACTOR = 1.03
DEFAULT_MIRROR_ENABLED = False
DEFAULT_CONVERT_TO_PORTRAIT = True

# Subtitle settings
DEFAULT_SUBTITLE_FONT_SIZE = 14
DEFAULT_SUBTITLE_COLOR = "white"
DEFAULT_SUBTITLE_OUTLINE = 3

# GPU Encoding Limiter - Prevent NVENC overload
# Increased from 10 to 100 to support batch processing of more videos
MAX_GPU_ENCODE_CONCURRENT = 100

# Background Processing
AUTO_MINIMIZE_ON_PROCESS = True  # Auto minimize to tray when processing starts
NOTIFY_PER_VIDEO = True  # Show notification after each video
NOTIFY_ON_COMPLETE = True  # Show notification when all videos are done

# Supported video extensions
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
