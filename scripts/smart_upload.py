
import os
import urllib.request
import urllib.parse
import sys
import random

# --- CONFIG ---
BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_ZONE_NAME = "kovertripweb"
BASE_URL = "https://storage.bunnycdn.com"

def upload_file(local_path, remote_path):
    # Properly encode the path. 
    # bunnycdn requires the path to be URL encoded, but NOT the slashes that separate directories
    # We split by slash, encode each component, then join safely.
    path_components = remote_path.split('/')
    encoded_components = [urllib.parse.quote(comp) for comp in path_components]
    safe_remote_path = "/".join(encoded_components)
    
    url = f"{BASE_URL}/{STORAGE_ZONE_NAME}/{safe_remote_path}"

    headers = {
        "AccessKey": BUNNY_API_KEY,
        "Content-Type": "application/octet-stream",
    }
    
    try:
        with open(local_path, "rb") as f:
            data = f.read()
            
        req = urllib.request.Request(url, data=data, headers=headers, method='PUT')
        with urllib.request.urlopen(req) as response:
            return response.status == 201
    except Exception as e:
        print(f"Error uploading {local_path}: {e}")
        return False

def smart_scout_and_upload(source_folder, bunny_folder_name, limit=10):
    print(f"🕵️‍♂️ Scouting folder: {source_folder}")
    
    if not os.path.exists(source_folder):
        print(f"❌ Error: Folder does not exist: {source_folder}")
        return

    candidates = []
    
    # Walk through folder recursively
    for root, dirs, files in os.walk(source_folder):
        # print(f"📂 Looking via {root}...")
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
                full_path = os.path.join(root, file)
                try:
                    # Check size to filter (and to ensure file is locally accessible)
                    size = os.path.getsize(full_path)
                    candidates.append((full_path, size))
                except OSError:
                    print(f"   ⚠️ Cannot read size (cloud file?): {file}")
                    print("      👉 Action Required: Please right-click folder in Finder and select 'Make Available Offline'")

    if not candidates:
        print("❌ No valid images found.")
        return

    print(f"📸 Found {len(candidates)} images. Picking top {limit} largest (highest quality)...")
    
    # Sort by size (largest first) -> Proxy for quality/resolution
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Take top N
    selected = candidates[:limit]
    
    print("🚀 Starting upload to Bunny.net...")
    
    uploaded_files = []
    
    for i, (path, size) in enumerate(selected):
        ext = os.path.splitext(path)[1].lower()
        if ext == '.heic':
            # Skip HEIC for web for now (browsers don't like it), or simple rename (risky)
            # ideally we should convert, but for now let's skip
            continue
            
        new_name = f"{bunny_folder_name}_{i+1}{ext}"
        remote_path = f"Двухдневка в Альпы/AutoSync/{bunny_folder_name}/{new_name}"
        
        print(f"[{i+1}/{len(selected)}] Uploading {os.path.basename(path)} -> {new_name}...")
        
        if upload_file(path, remote_path):
            # Construct public URL
            # Also encode for the browser
            public_path_components = remote_path.split('/')
            encoded_public_path = "/".join([urllib.parse.quote(comp) for comp in public_path_components])
            public_url = f"https://kovertrip.b-cdn.net/{encoded_public_path}"
            uploaded_files.append(public_url)
    
    print("\n✅ Upload Complete!")
    print("\n--- RESULTS ---")
    for url in uploaded_files:
        print(url)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        src = sys.argv[1]
    else:
        src = "/Users/dmitry/Library/CloudStorage/GoogleDrive-kover.trips@gmail.com/Мой диск/KOVER Media Content/Автобусные туры/Гальштат + Зальцбург"
    
    smart_scout_and_upload(src, "hallstatt_best", 10)
