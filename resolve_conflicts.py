import os

def resolve_dashboard():
    path = "app/assets/www/html/dashboard.html"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    out = []
    in_conflict = False
    keep_next = False
    
    for line in lines:
        if line.startswith("<<<<<<< HEAD"):
            in_conflict = True
            keep_next = False
            continue
        elif line.startswith("======="):
            keep_next = True
            continue
        elif line.startswith(">>>>>>>"):
            in_conflict = False
            keep_next = False
            continue
            
        if not in_conflict or keep_next:
            out.append(line)
            
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(out)

def resolve_workers():
    # For workers, we want our HEAD (the beautiful new UI)
    path = "app/assets/www/html/workers.html"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    out = []
    in_conflict = False
    keep_next = False
    
    for line in lines:
        if line.startswith("<<<<<<< HEAD"):
            in_conflict = True
            keep_next = True
            continue
        elif line.startswith("======="):
            keep_next = False
            continue
        elif line.startswith(">>>>>>>"):
            in_conflict = False
            keep_next = False
            continue
            
        if not in_conflict or keep_next:
            out.append(line)
            
    # Also we must make sure i18n.js is included in workers.html
    # Let's find </body> and insert it before
    final_out = []
    for line in out:
        if "</body>" in line and "i18n.js" not in "".join(out):
            final_out.append('    <script src="../js/i18n.js"></script>\n')
        final_out.append(line)
        
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(final_out)

resolve_dashboard()
resolve_workers()
