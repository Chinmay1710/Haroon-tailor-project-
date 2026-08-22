import os
from bs4 import BeautifulSoup

html_dir = "app/assets/www/html"
worker_tab_html = """<a class="flex items-center gap-3 px-3 py-3 rounded-lg text-on-primary/70 font-body-md hover:text-on-primary hover:bg-primary-container/20 transition-colors duration-200" href="#">
<span class="material-symbols-outlined">engineering</span>
<span class="font-label-lg text-label-lg">Workers</span>
</a>"""

for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(html_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        soup = BeautifulSoup(content, "html.parser")
        
        # Find the a tag that contains 'Workers'. If it exists, skip.
        if soup.find("a", string=lambda s: s and "Workers" in s):
            continue
            
        # Or look in its spans
        spans = soup.find_all("span", string=lambda s: s and "Workers" in s)
        if spans:
            continue

        # Find the Settings a tag
        settings_span = soup.find("span", string=lambda text: text and "Settings" in text.strip())
        
        if settings_span:
            settings_a = settings_span.find_parent("a")
            if settings_a:
                # Create the worker a tag
                worker_a = BeautifulSoup(worker_tab_html, "html.parser").a
                # Insert before the Settings a tag
                settings_a.insert_before(worker_a)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(str(soup))
                print(f"Injected into {filename}")
