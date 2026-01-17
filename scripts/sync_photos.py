
import os
import requests
import sys

# --- CONFIGURATION ---
BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_ZONE_NAME = "kovertripweb"
BASE_URL = "https://storage.bunnycdn.com"

# --- HELPERS ---
def upload_file(local_path, remote_path):
    """Uploads a single file to Bunny.net"""
    headers = {
        "AccessKey": BUNNY_API_KEY,
        "Content-Type": "application/octet-stream",
    }
    
    with open(local_path, "rb") as file_data:
        response = requests.put(
            f"{BASE_URL}/{STORAGE_ZONE_NAME}/{remote_path}",
            headers=headers,
            data=file_data
        )
        
    if response.status_code == 201:
        print(f"✅ Uploaded: {remote_path}")
        return True
    else:
        print(f"❌ Failed to upload {remote_path}: {response.status_code} - {response.text}")
        return False

def sync_folder(local_folder, target_folder_name):
    """
    Syncs images from local_folder to Bunny.net/target_folder_name 
    Renames them cleanly: target_folder_name_1.jpg, etc.
    """
    if not os.path.exists(local_folder):
        print(f"❌ Local folder not found: {local_folder}")
        return

    print(f"📂 Scanning: {local_folder}...")
    
    # Get all images
    files = [f for f in os.listdir(local_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4'))]
    files.sort() # Sort to keep order consistent-ish
    
    if not files:
        print("⚠️ No images found in local folder.")
        return

    print(f"found {len(files)} files. Starting upload to /{target_folder_name}/...")
    
    success_count = 0
    
    for index, filename in enumerate(files):
        extension = os.path.splitext(filename)[1].lower()
        new_filename = f"{target_folder_name}_{index + 1}{extension}"
        
        # Determine remote path (e.g. "Двухдневка в Альпы/hotel_1.jpg")
        # NOTE: Using a subfolder in Bunny for cleanliness
        remote_path = f"Двухдневка в Альпы/AutoSync/{target_folder_name}/{new_filename}"
        
        local_file_path = os.path.join(local_folder, filename)
        
        if upload_file(local_file_path, remote_path):
            success_count += 1

    print(f"🎉 Done! Uploaded {success_count} files.")
    print("Now you can update your HTML to point to this folder.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 sync_photos.py <LOCAL_FOLDER_PATH> <TARGET_NAME_IN_BUNNY>")
        print("Example: python3 sync_photos.py '/Users/dmitry/GoogleDrive/Alps/Hotel' 'hotel'")
        sys.exit(1)
        
    local_path = sys.argv[1]
    target_name = sys.argv[2]
    
    sync_folder(local_path, target_name)
