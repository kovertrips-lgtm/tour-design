import os
import re

# FILES
FILES = [
    "Двухдневка в Альпы/Mobile_Version/01_Hero_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/02_Program_Mobile.html",
    "Двухдневка в Альпы/Mobile_Version/03_Reviews_Mobile.html",
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
    body_content = body_match.group(1) if body_match else ""
    
    # Strip styles from body content to avoid duplication
    body_content = re.sub(r'<style[^>]*>.*?</style>', '', body_content, flags=re.DOTALL)
    
    return styles, body_content

all_styles = []
main_html_parts = []
widget_html_parts = []

# --- 1. CSS BASICS (RESPONSIVE) ---
wrapper_css = """
   /* Tilda Adaptive Wrapper - Responsive */
   .kover-mobile-wrapper {
       width: 100%;
       min-height: 100vh;
       background: #111; 
       position: relative;
       overflow-x: hidden;
       padding-bottom: 80px; /* Space for FAB */
   }

   /* Default Mobile Styles used in HTML... */

   /* DESKTOP OVERRIDES (> 768px) */
   @media (min-width: 768px) {
       body {
           background-color: #111 !important; /* Unified Dark Background */
       }

       .kover-mobile-wrapper {
           max-width: 1200px; /* Wide Container */
           margin: 0 auto;
           border: none;
           box-shadow: none;
       }

       #t-footer { display: none; } 

       /* HERO DESKTOP */
       .m-hero {
           height: 90vh; /* Taller hero */
           border-radius: 0 0 40px 40px;
       }
       .m-hero-content {
           align-items: center;
           text-align: center;
           padding: 60px;
           max-width: 800px;
           margin: 0 auto;
       }
       .m-title {
           font-size: 64px; /* Bigger Title */
       }
       .m-subtitle {
           font-size: 20px;
           max-width: 600px;
       }
       .m-cta-btn {
           width: auto;
           padding: 20px 60px;
           font-size: 18px;
       }

       /* PROGRAM & REVIEWS GRID aka "Not Mobile Scroll" */
       .m-prog-scroll, 
       .m-reviews-scroll {
           display: flex; /* Grid-like Flex */
           flex-wrap: wrap;
           justify-content: center;
           padding: 0 40px 60px !important;
           overflow: visible !important;
       }

       .m-story-card,
       .m-review-card {
           flex: 0 1 300px; /* Flexible width but around 300px */
           margin-bottom: 20px;
       }

       /* ORG DETAILS GRID */
       .m-org-section {
           display: grid;
           grid-template-columns: 1fr 1fr;
           gap: 40px;
           max-width: 1000px;
           margin: 0 auto;
           padding-bottom: 120px; /* Space for FAB */
       }
       .m-org-header {
           grid-column: 1 / -1;
       }
       
       /* FLOATING CTA ON DESKTOP */
       .m-float-cta {
           width: auto !important;
           min-width: 300px;
           left: 50% !important;
           transform: translateX(-50%) !important;
           bottom: 30px !important;
           position: fixed !important;
       }

       /* POPUPS */
       .popup-overlay {
           align-items: center !important; /* Center modal */
           padding: 40px !important;
       }
       .popup-content {
           border-radius: 20px !important;
           max-width: 800px !important;
           height: auto !important;
           max-height: 90vh !important;
           display: flex;
           flex-direction: row; /* Side-by-side content? Or just wider vertical? */
           overflow: hidden;
       }
       /* We keep popup content simple for now, maybe just wider */
       
       /* Widget Modal */
       .widget-container {
           max-width: 900px !important; /* Wider widget */
           height: 700px !important;
           flex-direction: row !important; /* Side-by-side steps? No, logic is mobile. Keep it centered box */
           max-width: 450px !important; /* actually keep widget narrow/phone-sized, standard practice */
       }
   }
"""
all_styles.append(wrapper_css)

# --- 2. GATHER CONTENT ---
for fp in FILES:
    s, b = extract_content(fp)
    all_styles.extend(s)
    main_html_parts.append(f"\n<!-- SOURCE: {fp} -->\n")
    main_html_parts.append(b)

for fp in WIDGET_FILES:
    s, b = extract_content(fp)
    # Widget Core styles make up a huge chunk, we add them to styles
    all_styles.extend(s)
    widget_html_parts.append(f"\n<!-- SOURCE: {fp} -->\n")
    widget_html_parts.append(b)

# --- 3. GENERATE FILES ---

# BLOCK 1: CSS & DEPENDENCIES
with open("tilda_block_1_css.html", "w", encoding='utf-8') as f:
    f.write("<!-- BLOCK 1: CSS & HEAD -->\n")
    f.write("""
<script src="https://js.stripe.com/v3/"></script>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/css/intlTelInput.css">
<script src="https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/intlTelInput.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/ru.js"></script>
    """)
    f.write("<style>\n")
    f.write("\n".join(all_styles))
    f.write("\n</style>\n")

# BLOCK 2: MAIN HTML CONTENT
with open("tilda_block_2_content.html", "w", encoding='utf-8') as f:
    f.write("<!-- BLOCK 2: MAIN CONTENT -->\n")
    f.write('<div class="kover-mobile-wrapper">\n')
    f.write("\n".join(main_html_parts))
    f.write('\n</div><!-- END WRAPPER -->\n')

# BLOCK 3: WIDGET (LOGIC + TEMPLATES)
with open("tilda_block_3_widget.html", "w", encoding='utf-8') as f:
    f.write("<!-- BLOCK 3: WIDGET & JS -->\n")
    f.write("\n".join(widget_html_parts))

print("Done! Created 3 files: tilda_block_1_css.html, tilda_block_2_content.html, tilda_block_3_widget.html")
