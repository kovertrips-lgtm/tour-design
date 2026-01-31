
import os

ROOT_DIRS = [
    r"Двухдневка в Альпы",
    r"Двухдневка в Альпы/Mobile_Version"
]

WRONG_PATTERN = "https://kovertrip.b-cdn.net/https://kovertrip.b-cdn.net/"
CORRECT_PATTERN = "https://kovertrip.b-cdn.net/"

def fix_double_urls():
    print("Fixing double URL prefixes...")
    
    for d in ROOT_DIRS:
        if not os.path.exists(d):
            continue
            
        for filename in os.listdir(d):
            if filename.endswith(".html"):
                filepath = os.path.join(d, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if WRONG_PATTERN in content:
                    print(f"Fixing {filename}...")
                    new_content = content.replace(WRONG_PATTERN, CORRECT_PATTERN)
                    # Just in case of triple? Loop until clean? No, simple replace is enough for now.
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == "__main__":
    fix_double_urls()
