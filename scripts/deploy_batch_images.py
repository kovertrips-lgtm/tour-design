import urllib.request
import urllib.parse
import os

# CONFIG
BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_ZONE_NAME = "kovertripweb"
BASE_URL = "https://storage.bunnycdn.com"

# Define files to upload with local path and remote path
FILES_TO_UPLOAD = [
    # RED BULL (Adding bull2, bull4 mentioned by user)
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/bull2.jpg",
        "remote": "Двухдневка в Альпы/RedBull/bull2.jpg"
    },
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/bull4.jpg",
        "remote": "Двухдневка в Альпы/RedBull/bull4.jpg"
    },
    
    # HOTEL IMAGES
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/805943864.jpg",
        "remote": "Двухдневка в Альпы/Hotel/805943864.jpg"
    },
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/332735359.jpg",
        "remote": "Двухдневка в Альпы/Hotel/332735359.jpg"
    },
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/514073860.jpg",
        "remote": "Двухдневка в Альпы/Hotel/514073860.jpg"
    },
     # Assuming this one exists based on usage in code, though not in list_dir? 
     # Wait, list_dir showed 27 files. Let's check if 514073855.jpg exists.
     # It wasn't in list_dir output. It might be missing locally.
     # Let's try to upload what we have confirmed in list_dir:
     # 332735359.jpg, 514073860.jpg, 805943864.jpg are in list_dir.
     # 564538598.jpg, 689149855.jpg, 804959493.jpg, 804959505.jpg are also there.
     # alpine_hotel.png is there.
]

def upload_file(local_path, remote_path):
    print(f"🚀 Uploading {os.path.basename(local_path)} to {remote_path}...")
    
    if not os.path.exists(local_path):
        print(f"❌ Local file not found: {local_path}")
        return False

    # Encode path components
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
            if response.status == 201:
                print("✅ Success!")
                return True
            else:
                print(f"⚠️ Unexpected status: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Error uploading {local_path}: {e}")
        return False

if __name__ == "__main__":
    print("--- STARTING BATCH UPLOAD ---")
    for item in FILES_TO_UPLOAD:
        upload_file(item["local"], item["remote"])
    print("--- DONE ---")
