
import os
import re
import requests
from PIL import Image
from io import BytesIO
import urllib.parse

# Configuration
PROJECT_DIR = r"c:\Users\ddlou\OneDrive\Documents\Antigravity\Двухдневка в Альпы"
CDN_DOMAIN = "kovertrip.b-cdn.net"
NEW_CDN_PATH = "https://kovertrip.b-cdn.net/images"

# BunnyCDN Config
API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_NAME = "kovertripweb"
BASE_URL = "https://storage.bunnycdn.com"
OUTPUT_DIR = "optimized_images_auto"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Track processed files to avoid re-uploading in one run
processed_map = {} # old_url -> new_url

def optimize_and_upload(url):
    try:
        if url in processed_map:
            return processed_map[url]

        # Check if already optimized format
        if "/images/" in url and url.endswith(".webp"):
            return url

        print(f"[Processing] {url}")
        
        # Download
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                print(f"  [Error] Failed to download (Status {resp.status_code})")
                return None
        except Exception as e:
            print(f"  [Error] Download exception: {e}")
            return None

        # Determine filename
        parsed = urllib.parse.urlparse(url)
        path = urllib.parse.unquote(parsed.path)
        filename = os.path.basename(path)
        name_no_ext = os.path.splitext(filename)[0]
        webp_filename = f"{name_no_ext}.webp"
        
        # Clean up filename (remove spaces, parentheses stuff if needed, but keeping simple for now)
        # Actually, let's keep it simple to match content, but Bunny handles spaces poorly sometimes?
        # Let's ensure filename is safe.
        # safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name_no_ext) 
        # But we want to preserve recognition. Let's stick to original name base.

        local_path = os.path.join(OUTPUT_DIR, webp_filename)

        # Convert
        try:
            img = Image.open(BytesIO(resp.content))
            if img.mode in ("RGBA", "LA"):
                fill_color = (255, 255, 255)
                background = Image.new(img.mode[:-1], img.size, fill_color)
                background.paste(img, img.split()[-1])
                img = background
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(local_path, "WEBP", quality=80)
        except Exception as e:
            print(f"  [Error] Image conversion failed: {e}")
            return None

        # Upload
        upload_url = f"{BASE_URL}/{STORAGE_NAME}/images/{webp_filename}"
        headers = {
            "AccessKey": API_KEY,
            "Content-Type": "application/octet-stream"
        }
        
        # Check if file exists on CDN (optional, skipping for speed/overwrite)
        # Just upload
        with open(local_path, 'rb') as f:
            put_resp = requests.put(upload_url, data=f, headers=headers)
            if put_resp.status_code != 201:
                print(f"  [Error] Upload failed: {put_resp.text}")
                return None

        new_url = f"{NEW_CDN_PATH}/{webp_filename}"
        print(f"  [Success] -> {new_url}")
        processed_map[url] = new_url
        return new_url

    except Exception as e:
        print(f"  [Error] Global processing error: {e}")
        return None

def process_files():
    for root, _, files in os.walk(PROJECT_DIR):
        for file in files:
            if file.endswith(".html"):
                full_path = os.path.join(root, file)
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all CDN URLs
                matches = re.findall(r'(https?://' + re.escape(CDN_DOMAIN) + r'/[^"\')\s>]+)', content)
                unique_matches = set(matches)
                
                new_content = content
                file_changed = False
                
                for url in unique_matches:
                    # Ignore if not image or already good
                    ext = os.path.splitext(url)[1].lower()
                    if ext not in ['.jpg', '.jpeg', '.png']:
                        continue
                    if "/images/" in url and ext == '.webp':
                        continue

                    # Optimize
                    new_url = optimize_and_upload(url)
                    
                    if new_url and new_url != url:
                        # Replace in content
                        new_content = new_content.replace(url, new_url)
                        file_changed = True
                
                if file_changed:
                    print(f"Updating references in {file}...")
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == "__main__":
    process_files()
