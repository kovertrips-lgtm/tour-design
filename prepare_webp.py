
import os
from PIL import Image

# Configuration
IMAGE_DIR = r"Двухдневка в Альпы/images"
QUALITY = 80

def convert_images():
    print(f"Starting conversion in {IMAGE_DIR}...")
    
    if not os.path.exists(IMAGE_DIR):
        print(f"Error: Directory {IMAGE_DIR} not found.")
        return

    files = os.listdir(IMAGE_DIR)
    count = 0
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(IMAGE_DIR, filename)
            name, ext = os.path.splitext(filename)
            new_filename = name + ".webp"
            new_filepath = os.path.join(IMAGE_DIR, new_filename)
            
            # Convert only if not exists (or force overwrite)
            try:
                with Image.open(filepath) as img:
                    img.save(new_filepath, 'webp', quality=QUALITY)
                    print(f"Created: {new_filename}")
                    count += 1
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")

    print(f"Done! Created {count} WebP images.")
    print("Please upload these .webp files to your Bunny.net storage.")

if __name__ == "__main__":
    convert_images()
