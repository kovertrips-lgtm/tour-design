import os

# SVG DEFINITIONS (from replace_emojis.py)
# We need to map SVG -> Emoji
SVGS_MAP = {
    # Calendar 📅
    '📅': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/></svg>',
    
    # Money/Bag 💸
    '💸': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>',

    # Bus 🚌
    '🚌': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M4 16c0 .88.39 1.67 1 2.22V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4s-8 .5-8 4v10zm3.5 1c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm9 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm1.5-6H6V6h12v5z"/></svg>',

    # Bagel/Food 🥯
    '🥯': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M20 3H4v10c0 2.21 1.79 4 4 4h6c2.21 0 4-1.79 4-4v-3h2c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 5h-2V5h2v3zM4 19h16v2H4z"/></svg>',

    # Brain/Team 🧠
    '🧠': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',

    # Camera 📸
    '📸': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/></svg>',
    '📷': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/></svg>',

    # Sled/Gondola 🚡
    '🚡': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M19 3H5v18h14V3zm-2 16H7V5h10v14z"/><path d="M13.5 13.5l1.5-1.5L12 9l-3 3 1.5 1.5L13.5 13.5z"/></svg>',
    '&#128679;': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M19 3H5v18h14V3zm-2 16H7V5h10v14z"/></svg>',

    # Plane ✈️
    '✈️': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>',

    # Gift 🎁
    '🎁': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-2 .89-2 2v12c0 1.1.89 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-5-2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM9 4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm11 15h-3v-8h3v8zm-5 0h-3v-8h3v8zm-5 0H7v-8h3v8zM4 19v-8h3v8H4z"/></svg>',

    # Check ✅
    '✅': '<svg class="emoji-svg" viewBox="0 0 24 24" style="color:#29B6F6;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',

    # Star ⭐
    '⭐': '<svg class="emoji-svg" viewBox="0 0 24 24" style="color:#FFC107;"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>',

    # Down 👇
    '👇': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z"/></svg>',

    # Rocket 🚀
    '🚀': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M12 2.5s-4 4.5-4 10.5c0 2.5 1.5 3 4 3 2.5 0 4-.5 4-3 0-6-4-10.5-4-10.5zm0 13c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/></svg>',

    # Coat 🧥
    '🧥': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M12 3L4 9v12h16V9l-8-6zm0 2.5L17.5 9H6.5L12 5.5zM12 11c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2z"/></svg>',

    # Cap 🧢
    '🧢': '<svg class="emoji-svg" viewBox="0 0 24 24"><path d="M3 15h18v2H3v-2zm0-4h18v2H3v-2zm0-4h18v2H3V7z"/></svg>'
}

# Reverse mapping: Key is the content to REPLACE (the SVG), Value is what we want (the Emoji)
REVERSE_MAP = {}
for emoji, svg_code in SVGS_MAP.items():
    if emoji and not emoji.startswith('&#'):
        REVERSE_MAP[svg_code] = emoji
    elif emoji.startswith('&#'):
        # Even if it's an entity, we prefer the unicode char if possible, or we just map it back
        # For this script w'll try to map exact strings.
        # But wait, python dicts are unique keys.
        # The SVGS_MAP in replace_emojis.py creates duplicates contents for entities.
        # So we just map content to emoji.
        # If we have duplicate SVGS for different entities, last one wins.
        # But here '✈️' and '&#9992;' have same SVG
        pass

# Manually ensure we catch all, simpler loop
for emoji, svg_code in SVGS_MAP.items():
    # If the key is an entity like &#123;, we still want the Emoji char if known?
    # Or just use the key. Let's use the key if it's a specific unique SVG.
    # Actually, simpler: map SVG code -> First Emoji Key found that isn't an entity, or entity if must.
    valid_emoji = emoji
    if emoji.startswith('&#'):
        # try to find a non-entity version in the keys with same value?
        # or just leave it.
        pass
    
    # We want to restore to the Unicode character usually.
    # Let's clean up our map
    target = emoji
    if target == '&#128184;': target = '💸'
    if target == '&#128652;': target = '🚌'
    if target == '&#129360;': target = '🥯'
    if target == '&#129504;': target = '🧠'
    if target == '&#128248;': target = '📸'
    if target == '&#128247;': target = '📷'
    if target == '&#128679;': target = '🚡'
    if target == '&#9992;': target = '✈️'
    if target == '&#9992;&#65039;': target = '✈️'
    if target == '&#127873;': target = '🎁'
    if target == '&#10004;': target = '✅'
    if target == '&#11088;': target = '⭐'
    if target == '&#128071;': target = '👇'
    if target == '&#128640;': target = '🚀'
    
    REVERSE_MAP[svg_code] = target


# CSS to remove
CSS_TO_REMOVE = """
<style>
/* GLOBAL SVG EMOJI STYLE */
.emoji-svg {
    width: 1.25em;
    height: 1.25em;
    vertical-align: -0.25em;
    fill: currentColor;
    display: inline-block;
}
</style>
"""

INLINE_CSS_REMOVE = ".emoji-svg { width: 1.25em; height: 1.25em; vertical-align: -0.25em; fill: currentColor; display: inline-block; }"

# Files to process
FILES = [
    "Двухдневка в Альпы/01_Hero.html",
    "Двухдневка в Альпы/02_Program.html",
    "Двухдневка в Альпы/08_Timeline.html",
    "Двухдневка в Альпы/09_OrgDetails.html",
    "Двухдневка в Альпы/Mobile_Version/01_Hero_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/02_Program_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/08_Timeline_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/09_OrgDetails_Mobile.html"
]

def restore_file(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content

    # 1. Start replacing content
    count = 0
    for svg_code, emoji in REVERSE_MAP.items():
        if svg_code in content:
            # We probably need to handle whitespace/newline variations if the SVG was formatted?
            # replace_emojis.py used exact strings from the dict. So exact match should work.
            scan_count = content.count(svg_code)
            if scan_count > 0:
                print(f"  Restoring {emoji} ({scan_count} times)")
                content = content.replace(svg_code, emoji)
                count += scan_count
    
    # 2. Cleanup CSS
    if CSS_TO_REMOVE.strip() in content:
        content = content.replace(CSS_TO_REMOVE.strip(), "")
    
    # Try generous removal of CSS block with newlines
    content = content.replace(CSS_TO_REMOVE, "")
    
    # Try cleaning inline CSS injections if any
    content = content.replace(INLINE_CSS_REMOVE, "")

    # Cleanup empty style tags if we left any
    content = content.replace("<style>\n\n</style>", "")
    content = content.replace("<style></style>", "")

    # Check if content actually changed
    if content != original_content:
        print(f"Updated {path}: Restored {count} emojis (and/or cleaned CSS)")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f"No changes made to {path}")

if __name__ == "__main__":
    print("Restoring Unicode Emojis...")
    for p in FILES:
        restore_file(p)
    print("Done.")
