# Kover Project Style Guide & Critical Instructions

## 1. Encoding & Emojis (CRITICAL)

### In HTML Structure:
**Rule:** NEVER use raw emojis (e.g., 👆, 🚀) directly in HTML code blocks.
**Reason:** Tilda's editor or database encoding often corrupts them into `?` or garbage characters.
**Solution:** ALWAYS use **HTML Decimal Entities**.

**Common Entities Table:**
- 👆 Tap/Touch: `&#128070;`
- → Right Arrow (Text): `&rarr;` or `&#8594;`
- 🚀 Rocket: `&#128640;`
- ⭐️ Star: `&#11088;`
- 📷 Camera: `&#128247;` (Note: Sometimes rendered better as `📷` if supported, but entities are safer)
- 📅 Calendar: `&#128197;`
- 💰 Money Bag: `&#128184;`
- ✓ Checkmark: `&#10003;`

### In CSS (`content` property):
**Rule:** NEVER use HTML Entities (like `&#10003;`) in CSS.
**Reason:** CSS does not parse HTML entities; it will display the literal text string.
**Solution:** Use **CSS Hex Escapes**.

**Example:**
*   ❌ Bad: `content: '&#10003;';`
*   ✅ Good: `content: '\2713';` (Checkmark)

---

## 2. Buttons & Colors in Tilda

### Forced Colors
**Rule:** When styling buttons that must have a specific text color (e.g., White text on Blue background), **ALWAYS use `!important`**.
**Reason:** Tilda's global styles often have high-specificity rules (like `#rec12345 a { color: ... }`) that will override your clean CSS classes unless you force them.

**Code Snippet:**
```css
.btn-primary {
    background-color: #29B6F6;
    color: #ffffff !important; /* Mandatory for Tilda */
}
```

### Button Arrows/Icons
If you need an arrow inside a button:
1.  **Use HTML Entity:** `<button>Book Now &rarr;</button>`
2.  **Use SVG:** If you need a specific style, embed the SVG inline within the button tag. Ensure `fill="currentColor"` so it takes the text color (white).

---

## 3. File Organization & Deployment

### Output Files for Tilda
Due to Tilda's character limit per block, the code is generated into **4 parts**:

1.  **`tilda_block_1_css.html`** → Insert into **HEAD** block or T123 (CSS/Fonts).
2.  **`tilda_block_2_part1_valid.html`** → Insert into first **T123** block (Hero, details).
3.  **`tilda_block_2_part2_valid.html`** → Insert into second **T123** block (Reviews, CTA).
4.  **`tilda_block_3_widget.html`** → Insert into **T123** block (Widget logic) + Widget settings.

**Note:** Always ensure `part1` comes before `part2` in the page layout.

