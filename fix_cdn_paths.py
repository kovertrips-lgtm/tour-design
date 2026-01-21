
import os
import re

# Configuration
ROOT_DIRS = [
    r"Двухдневка в Альпы",
    r"Двухдневка в Альпы/Mobile_Version"
]
CDN_BASE = "https://kovertrip.b-cdn.net/images/"

def update_cdn_paths():
    print("Normalizing CDN paths to:", CDN_BASE)
    
    # We will look for known webp filenames and ensure they point to CDN
    images_dir = r"Двухдневка в Альпы/images"
    if not os.path.exists(images_dir):
        print("Images dir not found, can't list files.")
        return
        
    known_images = [f for f in os.listdir(images_dir) if f.endswith('.webp')]
    
    for d in ROOT_DIRS:
        if not os.path.exists(d):
            continue
            
        for filename in os.listdir(d):
            if filename.endswith(".html"):
                filepath = os.path.join(d, filename)
                process_file(filepath, known_images)

def process_file(filepath, known_images):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # We need to replace PNG/JPG references with WebP CDN references too!
    # Because current state is Reverted (so code has .png/.jpg)
    
    for img_name_webp in known_images:
        base_name = os.path.splitext(img_name_webp)[0]
        
        # Extensions to look for in source code
        exts = ['.png', '.jpg', '.jpeg', '.webp']
        
        for ext in exts:
            old_filename = base_name + ext
            
            # Setup replacement target
            new_url = f"{CDN_BASE}{img_name_webp}"
            
            # Patterns to replace
            # 1. "images/filename.ext"
            # 2. "../images/filename.ext"
            # 3. "https://kovertrip.b-cdn.net/.../filename.ext" (old long path)
            
            # Complex long path (Old structure)
            complex_path_prefix = "https://kovertrip.b-cdn.net/%D0%94%D0%B2%D1%83%D1%85%D0%B4%D0%BD%D0%B5%D0%B2%D0%BA%D0%B0%20%D0%B2%20%D0%90%D0%BB%D1%8C%D0%BF%D1%8B/"
            
            # Replacements
            content = content.replace(f'"{complex_path_prefix}{old_filename}"', f'"{new_url}"')
            content = content.replace(f"'{complex_path_prefix}{old_filename}'", f"'{new_url}'")
            content = content.replace(f'({complex_path_prefix}{old_filename})', f'({new_url})')
            
            content = content.replace(f'"images/{old_filename}"', f'"{new_url}"')
            content = content.replace(f"'images/{old_filename}'", f"'{new_url}'")
            content = content.replace(f'images/{old_filename}', f'{new_url}') # risky? usually ok in css url()
            
            content = content.replace(f'"../images/{old_filename}"', f'"{new_url}"')
            content = content.replace(f"'../images/{old_filename}'", f"'{new_url}'")
            content = content.replace(f'../images/{old_filename}', f'{new_url}')

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {os.path.basename(filepath)}")

if __name__ == "__main__":
    update_cdn_paths()
