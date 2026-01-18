import os
import re

# FILES CONFIGURATION
DESKTOP_FILES = [
    "Двухдневка в Альпы/01_Hero.html",
    "Двухдневка в Альпы/02_Program.html",
    "Двухдневка в Альпы/03_Hallstatt.html",
    "Двухдневка в Альпы/04_Sledding.html",
    "Двухдневка в Альпы/05_Hotel.html",
    "Двухдневка в Альпы/06_RedBull.html",
    "Двухдневка в Альпы/07_Salzburg.html",
    "Двухдневка в Альпы/08_Timeline.html",
    "Двухдневка в Альпы/Mobile_Version/03_Reviews_Mobile.html",
    "Двухдневка в Альпы/09_OrgDetails.html"
]

MOBILE_FILES = [
    "Двухдневка в Альпы/Mobile_Version/01_Hero_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/02_Program_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/07_Bus_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/10_HowItWorks_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/03_Reviews_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/11_Team_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/08_Timeline_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/09_OrgDetails_Mobile.html"
]

WIDGET_FILES = [
    "Двухдневка в Альпы/Widget_Config.html",
    "Двухдневка в Альпы/Widget_Core.html"
]

def extract_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    styles = []
    style_matches = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
    for s in style_matches:
        styles.append(s)
        
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
    if body_match:
        body_content = body_match.group(1)
    else:
        # If no body tag (fragment), remove styles and return rest
        body_content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        # Remove meta tags just in case
        body_content = re.sub(r'<meta[^>]*>', '', body_content)
    
    # Clean styles from body content again to be safe
    body_content = re.sub(r'<style[^>]*>.*?</style>', '', body_content, flags=re.DOTALL)
    
    return styles, body_content

all_styles = []
desktop_html_parts = []
mobile_html_parts = []
widget_html_parts = []

# --- 1. CSS BASICS ---
# We define a global wrapper logic to show/hide sections
wrapper_css = """
   /* UNIVERSAL WRAPPER LOGIC */
   .desktop-view {
       display: block;
   }
   .mobile-view {
       display: none;
   }
   
   @media (max-width: 900px) {
       .desktop-view {
           display: none;
       }
       .mobile-view {
           display: block;
           background: #111;
           min-height: 100vh;
       }
       body {
           background-color: #111 !important;
       }
   }
   
   @media (min-width: 901px) {
       body {
           background-color: #fff !important;
       }
       
       /* DESKTOP REVIEW GRID OVERRIDE */
       .m-reviews-section {
           background: #fff !important; /* Match desktop white theme */
       }
       .m-reviews-scroll {
           display: flex !important;
           flex-wrap: wrap !important;
           justify-content: center !important;
           overflow: visible !important;
           padding-bottom: 0 !important;
           gap: 30px !important;
           max-width: 1200px !important;
           margin: 0 auto !important;
       }
       .m-review-card {
           width: 300px !important;
           flex: none !important;
           margin-bottom: 30px !important;
           box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
           border: 1px solid #eee !important;
       }
   }
"""
all_styles.append(wrapper_css)

# --- 2. GATHER DESKTOP CONTENT ---
for fp in DESKTOP_FILES:
    s, b = extract_content(fp)
    all_styles.extend(s)
    desktop_html_parts.append(f"\n<!-- DESKTOP SOURCE: {fp} -->\n")
    desktop_html_parts.append(b)

# --- 3. GATHER MOBILE CONTENT ---
for fp in MOBILE_FILES:
    s, b = extract_content(fp)
    all_styles.extend(s)
    mobile_html_parts.append(f"\n<!-- MOBILE SOURCE: {fp} -->\n")
    mobile_html_parts.append(b)

# --- 4. GATHER WIDGET ---
for fp in WIDGET_FILES:
    s, b = extract_content(fp)
    all_styles.extend(s)
    widget_html_parts.append(f"\n<!-- WIDGET SOURCE: {fp} -->\n")
    widget_html_parts.append(b)

# --- 5. GENERATE FILES ---

# BLOCK 1: CSS & HEAD
with open("tilda_block_1_css.html", "w", encoding='utf-8') as f:
    f.write("<!-- BLOCK 1: CSS & HEAD -->\n")
    f.write("""
<script src="https://js.stripe.com/v3/"></script>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/css/intlTelInput.css">
<script src="https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/intlTelInput.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/ru.js"></script>
    """)
    f.write("<style>\n")
    f.write("\n".join(all_styles))
    f.write("\n</style>\n")

# BLOCK 2: MAIN CONTENT (DUAL VIEW)
with open("tilda_block_2_content.html", "w", encoding='utf-8') as f:
    f.write("<!-- BLOCK 2: MAIN CONTENT (DUAL VIEW) -->\n")
    
    # Desktop Wrapper
    f.write('<div class="desktop-view">\n')
    f.write("\n".join(desktop_html_parts))
    f.write('\n</div><!-- END DESKTOP -->\n')
    
    # Mobile Wrapper
    f.write('<div class="mobile-view">\n')
    f.write("\n".join(mobile_html_parts))
    f.write('\n</div><!-- END MOBILE -->\n')

# BLOCK 3: WIDGET
with open("tilda_block_3_widget.html", "w", encoding='utf-8') as f:
    f.write("<!-- BLOCK 3: WIDGET & JS -->\n")
    f.write("\n".join(widget_html_parts))

print("Done! Created 3 files with DUAL DESKTOP/MOBILE modes.")
