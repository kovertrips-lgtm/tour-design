
import os
import re

# Configuration
# Path to your project Root
ROOT_DIRS = [
    r"Двухдневка в Альпы",
    r"Двухдневка в Альпы/Mobile_Version"
]
CDN_BASE = "https://kovertrip.b-cdn.net/images/"

def update_cdn_paths():
    print("Normalizing CDN paths to:", CDN_BASE)
    
    # Regex to find image filenames ending in .webp
    # Capture group 1: filename.webp
    # We look for pattern: (something)/filename.webp
    # But result should be CDN_BASE + filename.webp
    
    img_pattern = re.compile(r'[\"\(\'](?:https?://[^\"\(\']+/|images/|../images/)?([a-zA-Z0-9_]+\.webp)[\"\)\']')

    for d in ROOT_DIRS:
        if not os.path.exists(d):
            continue
            
        for filename in os.listdir(d):
            if filename.endswith(".html"):
                filepath = os.path.join(d, filename)
                process_file(filepath, img_pattern)

def process_file(filepath, pattern):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Function to replace match
    def replacer(match):
        # match.group(0) is the full string like "url('.../file.webp')"
        # match.group(1) is "file.webp"
        
        full_match = match.group(0)
        filename = match.group(1)
        
        # Keep the quote/paren style
        start_char = full_match[0] # " or ' or (
        end_char = full_match[-1]
        
        # If it's a URL inside CSS url(), exclude quotes from base check
        # But regex captured quotes.
        
        return f"{start_char}{CDN_BASE}{filename}{end_char}"

    # Use re.sub with function
    # Because our regex captures the surrounding quotes, replace logic needs to be careful
    # My regex above: [\"\'\(] ... [\"\'\)]
    # Let's verify regex logic.
    
    # Better regex: Look for sources
    # src="...../foo.webp" -> src="CDN/foo.webp"
    # url('..../foo.webp') -> url('CDN/foo.webp')
    
    # Pattern: 
    # (src=|url\(|href=)(['"]?)(.*?)([a-zA-Z0-9_\-]+\.webp)(['"]?)
    # This is getting complex.
    
    # Simpler approach:
    # Just find all .webp filenames from our known list (we know them from the dir)
    # and force their prefix.
    
    images_dir = r"Двухдневка в Альпы/images"
    known_images = [f for f in os.listdir(images_dir) if f.endswith('.webp')]
    
    for img_name in known_images:
        # We want to replace ANY path pointing to this image with CDN path
        # Possible variations in code:
        # "images/file.webp"
        # "../images/file.webp"
        # "https://kovertrip.b-cdn.net/.../file.webp"
        
        # We can iterate and simply replace specific known wrong paths, or regex-replace any path ending in img_name
        
        # Regex: (['"(])([^'"()]*?)(file\.webp)(['")])
        # Replace group 2 with CDN_BASE_NO_PREFIX? No.
        
        # Let's do a reliable regex for each file
        # Escaped dot
        safe_name = re.escape(img_name)
        
        # Pattern: matches preceeding path chars until a quote, paren, or whitespace
        # But simpler: look for the filename, and check what's before it.
        # Replacing 'anything/filename.webp' with 'CDN/filename.webp' 
        
        # Regex:
        # (?<=["'\(])(.*?)(?=/?)(\b{safe_name}\b)
        # It's tricky.
        
        # Let's use the list of known files to construct simple string replacements for common patterns
        # 1. "images/{img}" -> "CDN/{img}"
        # 2. "../images/{img}" -> "CDN/{img}"
        # 3. "https://kovertrip.b-cdn.net/.../{img}" -> "CDN/{img}"
        
        # Specific known complex path from previous edit:
        complex_path_start = "https://kovertrip.b-cdn.net/%D0%94%D0%B2%D1%83%D1%85%D0%B4%D0%BD%D0%B5%D0%B2%D0%BA%D0%B0%20%D0%B2%20%D0%90%D0%BB%D1%8C%D0%BF%D1%8B/"
        
        content = content.replace(f'"{complex_path_start}{img_name}"', f'"{CDN_BASE}{img_name}"')
        content = content.replace(f"'{complex_path_start}{img_name}'", f"'{CDN_BASE}{img_name}'")
        content = content.replace(f'({complex_path_start}{img_name})', f'({CDN_BASE}{img_name})')
        
        content = content.replace(f'"images/{img_name}"', f'"{CDN_BASE}{img_name}"')
        content = content.replace(f"'images/{img_name}'", f"'{CDN_BASE}{img_name}'")
        content = content.replace(f'url(images/{img_name})', f'url({CDN_BASE}{img_name})')
        content = content.replace(f'url("images/{img_name}")', f'url("{CDN_BASE}{img_name}")')
        content = content.replace(f"url('images/{img_name}')", f"url('{CDN_BASE}{img_name}')")

        content = content.replace(f'"../images/{img_name}"', f'"{CDN_BASE}{img_name}"')
        content = content.replace(f"'../images/{img_name}'", f"'{CDN_BASE}{img_name}'")
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {os.path.basename(filepath)}")

if __name__ == "__main__":
    update_cdn_paths()
