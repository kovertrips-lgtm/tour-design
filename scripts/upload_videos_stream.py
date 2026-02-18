
import os
import requests
import json

LIBRARY_ID = "581522"
API_KEY = "0a7b10cc-bbbe-4b97-ac19260b44b3-92dc-48c7"
VIDEOS_DIR = "./videos"
PULL_ZONE = "vz-244f7910-31a"  # Based on existing URLs in HTML
BASE_URL = f"https://video.bunnycdn.com/library/{LIBRARY_ID}/videos"

def upload_video(filepath):
    filename = os.path.basename(filepath)
    print(f"Uploading {filename}...")

    # 1. Create Video
    headers = {
        "AccessKey": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {"title": filename}
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=data)
        if response.status_code != 200:
            print(f"Error creating video: {response.text}")
            return None
        
        video_id = response.json().get('guid')
        print(f"Created video ID: {video_id}")
    except Exception as e:
        print(f"Exception creating video: {e}")
        return None

    # 2. Upload File Content
    upload_url = f"{BASE_URL}/{video_id}"
    
    try:
        with open(filepath, 'rb') as f:
            file_data = f.read()
            
        response = requests.put(upload_url, headers=headers, data=file_data)
        if response.status_code != 200:
            print(f"Error uploading file content: {response.text}")
            return None
            
        print(f"Successfully uploaded {filename}")
        return video_id
    except Exception as e:
        print(f"Exception uploading file: {e}")
        return None

def main():
    if not os.path.exists(VIDEOS_DIR):
        print(f"Directory {VIDEOS_DIR} not found.")
        return

    files = [f for f in os.listdir(VIDEOS_DIR) if f.lower().endswith(('.mp4', '.mov'))]
    
    results = {}
    
    for f in files:
        filepath = os.path.join(VIDEOS_DIR, f)
        guid = upload_video(filepath)
        if guid:
            url = f"https://{PULL_ZONE}.b-cdn.net/{guid}/play_720p.mp4"
            results[f] = url
            print(f"URL: {url}")
            
    print("\n--- Summary ---")
    for fname, url in results.items():
        print(f"{fname} -> {url}")

if __name__ == "__main__":
    main()
