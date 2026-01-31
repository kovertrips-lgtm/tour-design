
import os
import requests

# BunnyCDN Configuration from found script
API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_ZONE_NAME = "kovertripweb"
BASE_URL = "https://storage.bunnycdn.com"
REGION = "" # If needed, usually empty for main region or "de", "ny" etc. But base url implies default.

# Local path
LOCAL_IMAGES_DIR = r"Двухдневка в Альпы/images"
# Remote path (in Bunny)
REMOTE_FOLDER = "images" 

def upload_files():
    if not os.path.exists(LOCAL_IMAGES_DIR):
        print(f"Error: Local directory {LOCAL_IMAGES_DIR} not found.")
        return

    files = [f for f in os.listdir(LOCAL_IMAGES_DIR) if f.endswith(".webp")]
    
    if not files:
        print("No .webp files found to upload. Please run prepare_webp.py first.")
        return

    print(f"Found {len(files)} WebP files. Uploading to /{STORAGE_ZONE_NAME}/{REMOTE_FOLDER}/...")

    headers = {
        "AccessKey": API_KEY,
        "Content-Type": "application/octet-stream"
    }

    success_count = 0

    for filename in files:
        local_path = os.path.join(LOCAL_IMAGES_DIR, filename)
        # Use simple slash for remote path
        remote_path = f"{STORAGE_ZONE_NAME}/{REMOTE_FOLDER}/{filename}"
        url = f"{BASE_URL}/{remote_path}"

        print(f"Uploading {filename}...", end=" ")
        
        try:
            with open(local_path, "rb") as f:
                data = f.read()
                
            response = requests.put(url, headers=headers, data=data)
            
            if response.status_code == 201:
                print("OK")
                success_count += 1
            else:
                print(f"FAILED ({response.status_code})")
                print(response.text)
        except Exception as e:
            print(f"ERROR: {e}")

    print("------------------------------------------------")
    print(f"Upload complete. {success_count}/{len(files)} files uploaded successfully.")

if __name__ == "__main__":
    upload_files()
