from utils.giphy_api import GiphyAPI
import json

def test():
    print("Testing Giphy API (Stickers)...")
    api = GiphyAPI()
    api.base_url = "https://api.giphy.com/v1/stickers/search"
    print(f"API Key: {api.api_key}")
    print(f"Base URL: {api.base_url}")
    
    query = "cat"
    print(f"Searching for '{query}'...")
    
    try:
        results = api.search_stickers(query, limit=5)
        print(f"Results found: {len(results)}")
        
        if results:
            print("First result:")
            print(json.dumps(results[0], indent=2))
        else:
            print("No results returned.")
            
    except Exception as e:
        print(f"Exception during search: {e}")

if __name__ == "__main__":
    test()
