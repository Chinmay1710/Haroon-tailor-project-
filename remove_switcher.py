import os
import glob
import re

html_dir = "app/assets/www/html"
html_files = glob.glob(os.path.join(html_dir, "*.html"))

# Regex to match the Language Switcher block. It starts with <!-- Language Switcher -->
# and we consume everything up to the closing </div> that matches the outer div.
# Since python regex doesn't easily do nested HTML parsing, we can just match up to the second </button>\n</div>
switcher_pattern = re.compile(r'<!-- Language Switcher -->\s*<div[^>]*>.*?</button>\s*</button>\s*</div>', re.DOTALL | re.IGNORECASE)

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    content = switcher_pattern.sub('', content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
print("Removed Language Switcher from all sidebars.")
