import os
import re

html_dir = "app/assets/www/html"
nav_item = """<a class="flex items-center gap-3 px-3 py-3 rounded-lg text-on-primary/70 font-body-md hover:text-on-primary hover:bg-primary-container/20 transition-colors duration-200" href="#">
<span class="material-symbols-outlined">engineering</span>
<span class="font-label-lg text-label-lg">Workers</span>
</a>
"""

for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(html_dir, filename)
        with open(filepath, "r") as f:
            content = f.read()
            
        if 'Workers</span>' not in content:
            # We look for the Settings tab to insert right before it
            # The setting tab looks like:
            # <a class="..." href="#">
            # <span class="material-symbols-outlined">settings</span>
            # <span class="font-label-lg text-label-lg">Settings</span>
            # </a>
            
            pattern = re.compile(r'(<a[^>]*href="#"[^>]*>\s*<span class="material-symbols-outlined">settings</span>\s*<span class="font-label-lg text-label-lg">Settings</span>\s*</a>)', re.DOTALL)
            
            if pattern.search(content):
                new_content = pattern.sub(nav_item + r'\1', content)
                with open(filepath, "w") as f:
                    f.write(new_content)
                    print(f"Injected into {filename}")
