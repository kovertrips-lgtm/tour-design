import os
import re

# FILES TO MERGE
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

OUTPUT_FILE = "code_for_tilda.html"

def extract_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract Style
    styles = []
    style_matches = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
    for s in style_matches:
        styles.append(s)
        
    # Extract Body Content (everything inside body)
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
    body_content = body_match.group(1) if body_match else ""
    
    # Remove script tags from body to move them to end? 
    # Actually, keep them in place or move them? 
    # Better to move them if they are libraries. 
    # But inline scripts (toggleVideo) should stay or be moved to end.
    # Let's keep them in body for now, but consolidate styles.
    
    # Remove the styles from body_content if they were inline? 
    # Regex found them anywhere. We should strip <style> tags from body_content.
    body_content = re.sub(r'<style[^>]*>.*?</style>', '', body_content, flags=re.DOTALL)
    
    return styles, body_content

all_styles = []
all_body_parts = []

# 1. External Deps (Fonts, Stripe)
all_body_parts.append("""
<!-- EXTERNAL DEPENDENCIES -->
<script src="https://js.stripe.com/v3/"></script>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/css/intlTelInput.css">
<script src="https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/intlTelInput.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/ru.js"></script>
""")

# 2. Add Wrapper Start
all_body_parts.append('<div class="kover-mobile-wrapper">')

# 3. Process Content Files
for fp in FILES:
    s, b = extract_content(fp)
    all_styles.extend(s)
    all_body_parts.append(f"<!-- SOURCE: {fp} -->")
    all_body_parts.append(b)

all_body_parts.append('</div><!-- END WRAPPER -->')

# 4. Process Widget (Outside Wrapper)
for fp in WIDGET_FILES:
    s, b = extract_content(fp)
    all_styles.extend(s)
    all_body_parts.append(f"<!-- SOURCE: {fp} -->")
    all_body_parts.append(b)

# 5. CSS Wrapper Logic
wrapper_css = """
   /* Tilda Adaptive Wrapper */
   .kover-mobile-wrapper {
       width: 100%;
       min-height: 100vh;
       background: #111; /* Default dark background matching content */
       position: relative;
       overflow-x: hidden;
   }
   
   @media (min-width: 768px) {
       body {
           background-color: #f4f5f7; /* Desktop background */
           display: flex;
           justify-content: center;
       }
       .kover-mobile-wrapper {
           max-width: 440px;
           margin: 0 auto; /* Center */
           box-shadow: 0 0 50px rgba(0,0,0,0.2);
           border-left: 1px solid #333;
           border-right: 1px solid #333;
       }
       /* Fix Fixed Elements to stick to wrapper */
       .m-float-cta {
           position: absolute !important; 
           /* This is tricky. Fixed elements are relative to viewport. 
              To make them relative to container, we need transforms, 
              but that breaks other fixed logic. 
              Alternative: restrict their max-width */
           max-width: 400px;
           left: 50% !important;
           transform: translateX(-50%) !important;
           bottom: 20px !important;
       }
       
       /* Fix Popups */
       .popup-overlay {
           /* Ensure popup overlay covers only the wrapper? 
              Usually popups are full screen. 
              If we want desktop experience, full screen popup is fine. 
              But center the content. */
       }
   }
"""

all_styles.insert(0, wrapper_css)

# WRITE OUTPUT
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("<!-- KOVER ANTI-GRAVITY GENERATED CODE -->\n")
    f.write("<style>\n")
    f.write("\n".join(all_styles))
    f.write("\n</style>\n")
    f.write("\n".join(all_body_parts))

print(f"Successfully created {OUTPUT_FILE} with size {os.path.getsize(OUTPUT_FILE)} bytes.")
