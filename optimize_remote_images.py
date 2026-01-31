
import os
import requests
from PIL import Image
from io import BytesIO

# Configuration
FILES_TO_PROCESS = [
    "https://kovertrip.b-cdn.net/%D0%94%D0%B2%D1%83%D1%85%D0%B4%D0%BD%D0%B5%D0%B2%D0%BA%D0%B0%20%D0%B2%20%D0%90%D0%BB%D1%8C%D0%BF%D1%8B/AutoSync/hallstatt_best/IMG_8703.jpg",
    "https://kovertrip.b-cdn.net/%D0%94%D0%B2%D1%83%D1%85%D0%B4%D0%BD%D0%B5%D0%B2%D0%BA%D0%B0%20%D0%B2%20%D0%90%D0%BB%D1%8C%D0%BF%D1%8B/Hallstatt/hall8.jpg",
    "https://kovertrip.b-cdn.net/%D0%94%D0%B2%D1%83%D1%85%D0%B4%D0%BD%D0%B5%D0%B2%D0%BA%D0%B0%20%D0%B2%20%D0%90%D0%BB%D1%8C%D0%BF%D1%8B/Hallstatt/hall4.jpg",
    "https://kovertrip.b-cdn.net/%D0%94%D0%B2%D1%83%D1%85%D0%B4%D0%BD%D0%B5%D0%B2%D0%BA%D0%B0%20%D0%B2%20%D0%90%D0%BB%D1%8C%D0%BF%D1%8B/Hallstatt/hall5.jpg",
    "https://kovertrip.b-cdn.net/%D0%94%D0%B2%D1%83%D1%85%D0%B4%D0%BD%D0%B5%D0%B2%D0%BA%D0%B0%20%D0%B2%20%D0%90%D0%BB%D1%8C%D0%BF%D1%8B/AutoSync/Salzburg/salzburg%20(19).jpg",
    "https://kovertrip.b-cdn.net/%D0%94%D0%B2%D1%83%D1%85%D0%B4%D0%BD%D0%B5%D0%B2%D0%BA%D0%B0%20%D0%B2%20%D0%90%D0%BB%D1%8C%D0%BF%D1%8B/AutoSync/Salzburg/IMG_6045.jpg",
    "https://kovertrip.b-cdn.net/%D0%94%D0%B2%D1%83%D1%85%D0%B4%D0%BD%D0%B5%D0%B2%D0%BA%D0%B0%20%D0%B2%20%D0%90%D0%BB%D1%8C%D0%BF%D1%8B/AutoSync/Salzburg/IMG_6013.jpg"
]

OUTPUT_DIR = "optimized_images"
API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_NAME = "kovertripweb"
BASE_URL = "https://storage.bunnycdn.com"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def process_and_upload():
    for url in FILES_TO_PROCESS:
        try:
            print(f"Downloading {url}...")
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to download {url}")
                continue

            # Load image
            img = Image.open(BytesIO(response.content))
            
            # Extract filename
            filename = url.split('/')[-1]
            filename = requests.utils.unquote(filename) # Decode URL encoded chars like %20
            name_no_ext = os.path.splitext(filename)[0]
            webp_filename = f"{name_no_ext}.webp"
            local_path = os.path.join(OUTPUT_DIR, webp_filename)

            # Convert to WebP
            print(f"Converting to {webp_filename}...")
            if img.mode in ("RGBA", "LA"):
                fill_color = (255, 255, 255)
                background = Image.new(img.mode[:-1], img.size, fill_color)
                background.paste(img, img.split()[-1])
                img = background

            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            img.save(local_path, "WEBP", quality=80)

            # Upload to Bunny
            print(f"Uploading {webp_filename} to BunnyCDN...")
            with open(local_path, 'rb') as file_data:
                upload_url = f"{BASE_URL}/{STORAGE_NAME}/images/{webp_filename}"
                headers = {
                    "AccessKey": API_KEY,
                    "Content-Type": "application/octet-stream"
                }
                response = requests.put(upload_url, data=file_data, headers=headers)
                
                if response.status_code == 201:
                    print(f"Success! Uploaded to https://kovertrip.b-cdn.net/images/{webp_filename}")
                else:
                    print(f"Upload failed: {response.text}")

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")

if __name__ == "__main__":
    process_and_upload()
