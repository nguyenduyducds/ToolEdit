import requests
import os
import shutil
from pathlib import Path

# GIPHY PUBLIC BETA KEY (Verify if it still works, otherwise user needs their own)
# This is a widely known public beta key, often rate limited but good for dev/test.
GIPHY_API_KEY = "rkDGgXPThsDXJcBnkPc290uPwZoJAXa8" 
# Alternative: User should ideally provide their own key in settings.

class GiphyAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key if api_key else GiphyAPI.get_api_key()
        self.base_url = "https://api.giphy.com/v1/stickers/search"
        self.temp_dir = Path("temp_stickers")
        self.temp_dir.mkdir(exist_ok=True)

    @staticmethod
    def get_api_key():
        # Standard Giphy Public Beta Key
        return "Gc7131jiJuvI7IdN0HZ1D7nh0ow5BU6g"

    def search_stickers(self, query, limit=12):
        """Search for stickers on Giphy"""
        try:
            params = {
                "api_key": self.api_key,
                "q": query,
                "limit": limit,
                "rating": "g",
                "lang": "en"
            }
            print(f"[DEBUG] Giphy Search URL: {self.base_url}")
            # print(f"[DEBUG] Params: {params}") # Don't print key in prod logs usually, but for debug ok
            
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get('data', []):
                    # Get the fixed_height_small url for preview (faster load)
                    # and original url for download
                    images = item.get('images', {})
                    preview_url = images.get('fixed_height_small', {}).get('url')
                    # Prefer standard static image for editing if available, else gif
                    # Use 'original' for best quality
                    full_url = images.get('original', {}).get('url')
                    
                    if preview_url and full_url:
                        results.append({
                            'id': item.get('id'),
                            'title': item.get('title'),
                            'preview_url': preview_url,
                            'full_url': full_url
                        })
                return results
            else:
                print(f"Giphy API Error: {response.status_code}")
                try: print(f"Response: {response.text}") 
                except: pass
                return []
        except Exception as e:
            print(f"Search Error: {e}")
            return []

    def download_sticker(self, url, sticker_id):
        """Download sticker to temp file"""
        try:
            print(f"[DEBUG] Download start: {sticker_id}")
            print(f"[DEBUG] URL: {url}")
            
            # Remove query parameters from URL before extracting extension
            url_without_params = url.split('?')[0] if '?' in url else url
            url_without_params = url_without_params.split('&')[0] if '&' in url_without_params else url_without_params
            
            # Extract extension from clean URL
            ext = url_without_params.split('.')[-1]
            if not ext or len(ext) > 4:  # Invalid extension
                ext = "gif"
            
            print(f"[DEBUG] Extension: {ext}")
            
            # Clean filename - only use sticker_id and extension
            filename = f"{sticker_id}.{ext}"
            filepath = self.temp_dir / filename
            
            print(f"[DEBUG] Target path: {filepath}")
            
            # If already downloaded, return path
            if filepath.exists():
                print(f"[DEBUG] Already exists, returning: {filepath}")
                return str(filepath)
            
            # Download the file
            print(f"[DEBUG] Downloading...")
            response = requests.get(url, stream=True, timeout=30)
            print(f"[DEBUG] Response status: {response.status_code}")
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
                
                print(f"[DEBUG] ✅ Download success: {filepath}")
                return str(filepath)
            else:
                print(f"[DEBUG] ❌ Download failed: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"[DEBUG] ❌ Download Error: {e}")
            import traceback
            traceback.print_exc()
            return None
