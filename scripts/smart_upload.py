
import os
import urllib.request
import sys
import random

# --- CONFIG ---
BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_ZONE_NAME = "kovertripweb"
BASE_URL = "https://storage.bunnycdn.com"

def upload_file(local_path, remote_path):
    url = f"{BASE_URL}/{STORAGE_ZONE_NAME}/{remote_path}"
    # Percent-encode the URL path to handle Spaces and Cyrillic safely
    # We split by '/' to encode each segment but keep slashes
    url_parts = url.split('/')
    # Everything after domain (parts[3:]) needs encoding
    # specifically the remote_path part which is at the end
    # Simpler approach: quote the remote_path part
    
    # Actually, simpler: just use urllib.request with headers
    # But we need to handle special chars in URL. 
    # Let's map remote_path manually
    safe_remote_path = urllib.parse.quote(remote_path)
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
        print(f"📂 Looking via {root}...")
        for file in files:
            print(f"   📄 File: {file}") # DEBUG PRINT
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
                full_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(full_path)
                    candidates.append((full_path, size))
                except OSError:
                    print(f"   ⚠️ Cannot read size (cloud file?): {file}")

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
            public_url = f"https://kovertrip.b-cdn.net/Двухдневка в Альпы/AutoSync/{bunny_folder_name}/{new_name}"
            uploaded_files.append(public_url)
    
    print("\n✅ Upload Complete!")
    print("\n--- RESULTS ---")
    for url in uploaded_files:
        print(url)

if __name__ == "__main__":
    src = "/Users/dmitry/Library/CloudStorage/GoogleDrive-kover.trips@gmail.com/Мой диск/KOVER Media Content/Автобусные туры/Гальштат + Зальцбург"
    smart_scout_and_upload(src, "hallstatt_best", 10)
