import os
import glob
import re

def resolve_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    if '<<<<<<< HEAD' not in content:
        return False
        
    filename = os.path.basename(filepath)
    
    pattern = re.compile(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> origin/vinit-work\n?', re.DOTALL)
    
    conflicts = list(pattern.finditer(content))
    if not conflicts:
        print(f"Warning: Could not parse conflicts in {filename}")
        return False
        
    print(f"Found {len(conflicts)} conflicts in {filename}")
    
    new_content = content
    for i in range(len(conflicts)-1, -1, -1):
        match = conflicts[i]
        head_content = match.group(1)
        vinit_content = match.group(2)
        
        keep_vinit = False
        if filename == 'customer_details.html' and i > 0:
            keep_vinit = True
            
        chosen_content = vinit_content if keep_vinit else head_content
        
        new_content = new_content[:match.start()] + chosen_content + "\n" + new_content[match.end():]

    with open(filepath, 'w') as f:
        f.write(new_content)
        
    print(f"Resolved {filename}")
    return True

html_files = glob.glob('app/assets/www/html/*.html')
resolved_count = 0
for f in html_files:
    if resolve_file(f):
        resolved_count += 1
        
print(f"Total files resolved: {resolved_count}")
