import os
import re

html_dir = "/Users/chinmay/Documents/Haroon_tailer/app/assets/www/html"

for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(html_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # We want to replace Artisan Stitch with <span class="global-shop-name">Artisan Stitch</span>
        # But we must avoid replacing it inside <title> tags.
        
        titles = re.findall(r'<title>.*?</title>', content, flags=re.IGNORECASE | re.DOTALL)
        for i, title in enumerate(titles):
            content = content.replace(title, f"__TITLE_PLACEHOLDER_{i}__")
            
        # Clean up any existing wraps to avoid nesting
        content = content.replace('<span class="global-shop-name">Artisan Stitch</span>', 'Artisan Stitch')
        content = content.replace('global-shop-name">Artisan Stitch', '">Artisan Stitch')
        
        # Now do the replacement
        content = content.replace('Artisan Stitch', '<span class="global-shop-name">Artisan Stitch</span>')
        
        # Put titles back
        for i, title in enumerate(titles):
            content = content.replace(f"__TITLE_PLACEHOLDER_{i}__", title)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
print("Successfully injected global shop name classes into HTML files.")
