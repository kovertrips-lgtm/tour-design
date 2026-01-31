
import os

BLOCK_1 = "tilda_block_1_css.html"
BLOCK_2_P1 = "tilda_block_2_part1_valid.html"
BLOCK_2_P2 = "tilda_block_2_part2_valid.html"
BLOCK_3 = "tilda_block_3_widget.html"
OUTPUT = "preview.html"

def read_file(path):
    if not os.path.exists(path):
        return f"<!-- MISSING: {path} -->"
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("Generating full preview.html from tilda blocks...")
    
    html = []
    html.append("<!DOCTYPE html><html lang='ru'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Kover Tour Preview</title></head><body>")
    
    # 1. Styles
    html.append("<!-- STYLES -->")
    html.append(read_file(BLOCK_1))
    
    # 2. Content
    html.append("<!-- CONTENT PART 1 -->")
    html.append(read_file(BLOCK_2_P1))
    
    html.append("<!-- CONTENT PART 2 -->")
    html.append(read_file(BLOCK_2_P2))
    
    # 3. Scripts
    html.append("<!-- SCRIPTS -->")
    html.append(read_file(BLOCK_3))
    
    html.append("</body></html>")
    
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write("\n".join(html))
        
    print(f"Success! {OUTPUT} created.")

if __name__ == "__main__":
    main()
