import re

with open("app/ui/web_bridge.py", "r") as f:
    content = f.read()

# We need to replace the entire create_backup and restore_backup block
match = re.search(r'(elif action == "create_backup":.*)else:\n\s+response = {"status": "error", "message": f"Unknown action: {action}"}', content, re.DOTALL)

if match:
    old_block = match.group(1)
    new_block = """elif action == "create_backup":
                from PySide6.QtWidgets import QFileDialog
                import shutil, os
                from datetime import datetime
                from app.config import DATABASE_PATH
                from app.database.engine import get_session
                from app.repositories.settings_repo import SettingsRepository
                
                db_path = DATABASE_PATH
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = f"TailorBackup_{timestamp}.db"
                
                # Ask for Hard Drive location
                save_path, _ = QFileDialog.getSaveFileName(self.parent(), "Save Backup File", default_filename, "Database Files (*.db)")
                
                if save_path:
                    shutil.copy2(db_path, save_path)
                    
                    # Handle Google Drive Backup
                    session = get_session()
                    try:
                        repo = SettingsRepository(session)
                        settings = repo.get_settings()
                        gdrive_path = getattr(settings, "backup_location", None)
                        
                        # Ensure it's an absolute path and exists, otherwise prompt again
                        if not gdrive_path or not os.path.exists(gdrive_path):
                            gdrive_path = QFileDialog.getExistingDirectory(self.parent(), "Select your local Google Drive folder for Automatic Backups (Cancel to skip)")
                            if gdrive_path:
                                repo.update_settings(backup_location=gdrive_path)
                                session.commit()
                        
                        if gdrive_path and os.path.exists(gdrive_path):
                            gdrive_backup = os.path.join(gdrive_path, default_filename)
                            shutil.copy2(db_path, gdrive_backup)
                            response = {"status": "success", "data": {"path": f"Hard Drive: {save_path}\\nGoogle Drive: {gdrive_backup}"}}
                        else:
                            response = {"status": "success", "data": {"path": save_path}}
                    finally:
                        session.close()
                else:
                    response = {"status": "error", "message": "Backup cancelled"}

            elif action == "restore_backup":
                from PySide6.QtWidgets import QFileDialog
                import shutil, os
                from app.config import DATABASE_PATH
                
                db_path = DATABASE_PATH
                
                # Ask user to select the .db file
                restore_path, _ = QFileDialog.getOpenFileName(self.parent(), "Select Backup File to Restore", "", "Database Files (*.db)")
                
                if restore_path and os.path.exists(restore_path):
                    shutil.copy2(restore_path, db_path)
                    response = {"status": "success", "data": {}}
                else:
                    response = {"status": "error", "message": "Restore cancelled or file not found"}

            """
    content = content.replace(old_block, new_block)
    with open("app/ui/web_bridge.py", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("Match not found")
