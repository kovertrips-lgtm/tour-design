import urllib.request
import urllib.parse
import os

# CONFIG
BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_ZONE_NAME = "kovertripweb"
BASE_URL = "https://storage.bunnycdn.com"

# Define files to upload with local path and remote path
FILES_TO_UPLOAD = [
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/hall2.jpg",
        "remote": "Двухдневка в Альпы/Hallstatt/hall2.jpg"
    },
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/hall4.jpg",
        "remote": "Двухдневка в Альпы/Hallstatt/hall4.jpg"
    },
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/hall5.jpg",
        "remote": "Двухдневка в Альпы/Hallstatt/hall5.jpg"
    },
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/hall6.jpg",
        "remote": "Двухдневка в Альпы/Hallstatt/hall6.jpg"
    },
    {
        "local": "/Users/dmitry/Documents/Kover Antigravity /Двухдневка в Альпы/images/hall8.jpg",
        "remote": "Двухдневка в Альпы/Hallstatt/hall8.jpg"
    }
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
    print("--- STARTING HALLSTATT UPLOAD ---")
    for item in FILES_TO_UPLOAD:
        upload_file(item["local"], item["remote"])
    print("--- DONE ---")
