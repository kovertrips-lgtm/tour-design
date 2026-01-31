
import os
import re

SEARCH_DIR = r"c:\Users\ddlou\OneDrive\Documents\Antigravity\Двухдневка в Альпы"
CDN_DOMAIN = "kovertrip.b-cdn.net"

# Set of unique image URLs found
image_urls = set()

def scan_html_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Find matches like src="https://kovertrip.b-cdn.net/..."
                    # We capture until the ending quote
                    matches = re.findall(r'src=["\'](https?://' + re.escape(CDN_DOMAIN) + r'/[^"\']+)["\']', content)
                    for url in matches:
                        # Filter out already optimized paths if you want, but better to check all source JPGs
                        if "/images/" not in url or not url.endswith(".webp"):
                             image_urls.add(url)

scan_html_files(SEARCH_DIR)

print("Found non-optimized images:")
for url in sorted(image_urls):
    print(f'    "{url}",')
