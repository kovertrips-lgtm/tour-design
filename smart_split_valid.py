import re
import os

INPUT_FILE = "tilda_block_2_content.html"
PART1_FILE = "tilda_block_2_part1_valid.html"
PART2_FILE = "tilda_block_2_part2_valid.html"

# Emoji map (simple replacement for common ones based on StyleGuide)
# We can extend this list
EMOJI_MAP = {
    "👆": "&#128070;",
    "🚀": "&#128640;",
    "⭐️": "&#11088;",
    "🏎": "&#127950;",
    "☕️": "&#9749;",
    "📸": "&#128248;",
    "📷": "&#128247;",
    "🚌": "&#128652;",
    "🧠": "&#129504;",
    "🥘": "&#129360;",
    "🛷": "&#128679;",
    "✈": "&#9992;",
    "🎁": "&#127873;",
    "✔️": "&#10004;",
    "✅": "&#9989;",
    "💰": "&#128184;",
    "📅": "&#128197;",
    "💸": "&#128184;",
    "📍": "&#128205;",
    "🏰": "&#127984;", 
    "🏔": "&#127956;",
    "❄": "&#10052;",
    "🇦🇹": "🇦🇹" # Flags usually survive or are font dependent, but leaving as is for now
}

def replace_emojis(text):
    # Basic replacements
    for char, entity in EMOJI_MAP.items():
        text = text.replace(char, entity)
    return text

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run dual_mode_tilda.py first.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix Emojis
    content = replace_emojis(content)

    # 2. Split logic
    # Target split point is roughly half
    mid_point = len(content) // 2
    
    # We look for a safe split point near middle. 
    # Ideal split: Between desktop and mobile wrappers? 
    # Or just between sections.
    
    # Let's try to find the boundary between Desktop and Mobile wrappers first.
    # The dual_mode script writes: </div><!-- END DESKTOP -->\n<div class="mobile-view">
    
    split_marker = '</div><!-- END DESKTOP -->'
    split_idx = content.find(split_marker)
    
    if split_idx != -1:
        # Include the closing div in Part 1
        split_idx += len(split_marker)
        print("Splitting exactly between Desktop and Mobile versions.")
    else:
        # Fallback: Find a closing div near middle
        # Search for "\n<!--" near middle (section comments)
        # Search range: +/- 20% from middle
        search_start = int(mid_point * 0.8)
        search_end = int(mid_point * 1.2)
        
        # Look for section comment
        match = re.search(r'\n<!--', content[search_start:search_end])
        if match:
            split_idx = search_start + match.start()
            print("Splitting at a section comment near middle.")
        else:
            print("Warning: Could not find clean split point. Splitting blindly at middle (risky).")
            split_idx = mid_point

    part1 = content[:split_idx]
    part2 = content[split_idx:]

    # Remove any internal STYLE tags if they snuck in (dual_mode script should have handled it, but double check)
    # Actually dual_mode keeps styles in block 1, so this should be clean HTML.

    with open(PART1_FILE, 'w', encoding='utf-8') as f:
        f.write(part1)
    
    with open(PART2_FILE, 'w', encoding='utf-8') as f:
        f.write(part2)

    print(f"Success! Created {PART1_FILE} ({len(part1)} bytes) and {PART2_FILE} ({len(part2)} bytes).")

if __name__ == "__main__":
    main()
