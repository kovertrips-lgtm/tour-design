# Kover Project Style Guide & Rules

## 1. Encoding & Emojis
**Rule:** NEVER use raw emojis (e.g., 👆, 🚀, ⭐️) in HTML files.
**Reason:** Tilda and some browsers may have encoding issues causing them to render as question marks (????) or replacement characters.
**Solution:** ALWAYS use HTML Decimal Entities.

**Reference Table:**
- 👆 Tap/Touch: `&#128070;`
- 🚀 Rocket: `&#128640;`
- ⭐️ Star: `&#11088;`
- 🏎 Race Car: `&#127950;`
- ☕️ Coffee: `&#9749;`
- 📸 Camera: `&#128248;`
- 🚌 Bus: `&#128652;`
- 🧠 Brain (Team): `&#129504;`
- 🥘 Food/Pan: `&#129360;`
- 🛷 Sled: `&#128679;`
- ✈️ Airplane: `&#9992;&#65039;` (Sometimes requires variation selector)
- 🎁 Gift: `&#127873;`
- ✔️ Check: `&#10004;`
- 💰 Money Bag: `&#128184;`
- 📅 Calendar: `&#128197;`

## 2. File Organization
- **Desktop/Mobile Split:** The project uses a "Dual Mode" setup.
- **Desktop Files:** Located in `Двухдневка в Альпы/` (root of trip folder).
- **Mobile Files:** Located in `Двухдневка в Альпы/Mobile_Version/`.
- **Assembly:** Use `dual_mode_tilda.py` to combine them into Tilda-ready blocks.

## 3. Tilda Integration
- Code is split into 3 blocks to avoid character limits:
  1. `tilda_block_1_css.html` (Styles, Head, Libs)
  2. `tilda_block_2_content.html` (HTML Content with Desktop/Mobile classes)
  3. `tilda_block_3_widget.html` (JS Widget logic)
