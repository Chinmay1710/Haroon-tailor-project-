import sys
import os

config_path = "app/config.py"
with open(config_path, "r") as f:
    content = f.read()

if "UPLOADS_DIR =" not in content:
    content = content.replace("BACKUP_DEFAULT_DIR = os.path.join(APP_DATA_DIR, \"backups\")", 
                              "BACKUP_DEFAULT_DIR = os.path.join(APP_DATA_DIR, \"backups\")\nUPLOADS_DIR = os.path.join(APP_DATA_DIR, \"uploads\")")
    content = content.replace("for d in [APP_DATA_DIR, DATABASE_DIR, LOG_DIR, BACKUP_DEFAULT_DIR]:",
                              "for d in [APP_DATA_DIR, DATABASE_DIR, LOG_DIR, BACKUP_DEFAULT_DIR, UPLOADS_DIR]:")
    
    with open(config_path, "w") as f:
        f.write(content)
    print("Updated app/config.py")
else:
    print("Already updated")
