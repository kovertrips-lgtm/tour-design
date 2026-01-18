
import requests
import json

LIBRARY_ID = "581522"
API_KEY = "0a7b10cc-bbbe-4b97-ac19260b44b3-92dc-48c7"
BASE_URL = f"https://video.bunnycdn.com/library/{LIBRARY_ID}/videos"

def get_videos():
    headers = {
        "AccessKey": API_KEY,
        "Accept": "application/json"
    }
    
    response = requests.get(BASE_URL, headers=headers)
    
    if response.status_code == 200:
        videos = response.json().get('items', [])
        print(f"✅ Found {len(videos)} videos:")
        for v in videos:
            print(f"- Title: {v['title']}")
            print(f"  ID: {v['guid']}")
            print(f"  Thumb: https://{LIBRARY_ID}.b-cdn.net/{v['guid']}/thumbnail.jpg")
            print("---")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    get_videos()
