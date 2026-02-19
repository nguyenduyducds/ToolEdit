"""Update checker functionality"""

import requests
from config.settings import APP_VERSION, UPDATE_URL


def check_for_updates():
    """Check for updates from remote JSON
    
    Returns:
        dict: Update information or None if no update available
    """
    try:
        response = requests.get(UPDATE_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("version", "0.0.0")
            download_url = data.get("download_url", "")
            message = data.get("message", "New version available!")
            
            # Check version (simple string comparison)
            if latest_version > APP_VERSION:
                return {
                    'version': latest_version,
                    'download_url': download_url,
                    'message': message
                }
        return None
    except Exception as e:
        print(f"Update check failed: {e}")
        return None
