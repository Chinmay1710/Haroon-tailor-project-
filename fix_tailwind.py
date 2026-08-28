import os
import glob
import re

html_files = glob.glob("app/assets/www/html/*.html")

for file in html_files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Remove the tailwind CSS script tag
    content = re.sub(r'<script src="\.\./js/tailwindcss\.js[^>]*></script>', '', content)
    
    # 2. Remove the tailwind config block
    content = re.sub(r'<script id="tailwind-config">.*?</script>', '', content, flags=re.DOTALL)
    
    # 3. Add the compiled CSS link right before </head> if it's not there
    if 'compiled.css' not in content:
        content = content.replace("</head>", '  <link rel="stylesheet" href="../css/compiled.css">\n</head>')
        
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print("Updated HTML files!")
