import os
import re

html_dir = "app/assets/www/html"
nav_item = """<a href="#" onclick="window.API.navigate('workers')" class="flex items-center gap-3 px-3 py-2 rounded-lg text-on-primary/70 hover:bg-white/10 hover:text-on-primary transition-colors group relative">
    <span class="material-symbols-outlined text-[20px]">engineering</span>
    <span class="font-label-md text-label-md">Workers</span>
</a>
"""

for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(html_dir, filename)
        with open(filepath, "r") as f:
            content = f.read()
            
        # We look for the last nav item before "Settings" or just after "Expenses"
        if 'navigate(\'workers\')' not in content:
            # Let's insert before Settings
            parts = re.split(r'(<a[^>]+onclick="window\.API\.navigate\(\'settings\'\)"[^>]*>.*?</a>)', content, flags=re.DOTALL)
            if len(parts) == 3:
                new_content = parts[0] + nav_item + parts[1] + parts[2]
                with open(filepath, "w") as f:
                    f.write(new_content)
