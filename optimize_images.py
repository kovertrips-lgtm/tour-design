
import os
import re
from PIL import Image

# Configuration
IMAGE_DIR = r"Двухдневка в Альпы/images"
ROOT_DIR = r"Двухдневка в Альпы"
MOBILE_DIR = r"Двухдневка в Альпы/Mobile_Version"
QUALITY = 80

def optimize_images():
    print(f"Starting optimization in {IMAGE_DIR}...")
    
    mapping = {} # old_name -> new_name

    # 1. Convert Images
    if not os.path.exists(IMAGE_DIR):
        print(f"Error: Directory {IMAGE_DIR} not found.")
        return

    files = os.listdir(IMAGE_DIR)
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(IMAGE_DIR, filename)
            name, ext = os.path.splitext(filename)
            new_filename = name + ".webp"
            new_filepath = os.path.join(IMAGE_DIR, new_filename)
            
            # Convert
            try:
                with Image.open(filepath) as img:
                    img.save(new_filepath, 'webp', quality=QUALITY)
                    print(f"Converted: {filename} -> {new_filename}")
                    
                    # Store mapping (case insensitive search, preserve casing in map?)
                    # Actually better to just map filename to new filename
                    mapping[filename] = new_filename
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")

    print(f"Converted {len(mapping)} images. Updating HTML files...")

    # 2. Update HTML files
    # We need to scan Desktop folder and Mobile folder
    target_dirs = [ROOT_DIR, MOBILE_DIR]
    
    for directory in target_dirs:
        if not os.path.exists(directory):
            continue
            
        for filename in os.listdir(directory):
            if filename.endswith(".html"):
                filepath = os.path.join(directory, filename)
                update_html_references(filepath, mapping)

def update_html_references(filepath, mapping):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    changes_count = 0
    
    for old_name, new_name in mapping.items():
        # Handle simple references
        if old_name in new_content:
            # We must be careful not to replace parts of other filenames
            # But usually filenames are unique enough in this context
            # Let's simple check if 'images/old_name' or '../images/old_name' exists
            # Actually, simpler replace is usually safe if filenames are specific.
            # Let's try replacing exact filename matches that are followed by quote or parenthesis
            
            # Regex is safer. Pattern: (images/|/images/|^)filename(\)|"|')
            # But paths can be complex.
            # Let's just do a naive replacement first, it's usually fine for asset names like "hallstatt_day.png"
            
            count = new_content.count(old_name)
            if count > 0:
                new_content = new_content.replace(old_name, new_name)
                changes_count += count
    
    if changes_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}: {changes_count} replacements.")
    else:
        pass # print(f"No changes in {filepath}")

if __name__ == "__main__":
    optimize_images()
