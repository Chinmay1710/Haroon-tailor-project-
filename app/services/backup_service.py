from __future__ import annotations
"""Backup service — SQLite file copy backup and restore."""

import os
import shutil
import glob
import zipfile
import tempfile
from datetime import datetime
from sqlalchemy import text

from app.config import DATABASE_PATH, BACKUP_DEFAULT_DIR, UPLOADS_DIR
from app.database.engine import get_session, close_db, init_db, get_engine
from app.repositories.settings_repo import SettingsRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BackupService:

    def create_backup(self, backup_dir: str = None) -> str:
        """
        Create a backup copy of the SQLite database and uploads into a ZIP.
        Deletes old backups in the target directories to keep only ONE file.
        Saves to both hard drive (BACKUP_DEFAULT_DIR) and Google Drive (if configured).
        """
        hard_drive_dir = BACKUP_DEFAULT_DIR
        gdrive_dir = None
        
        session = get_session()
        try:
            repo = SettingsRepository(session)
            settings = repo.get_settings()
            if settings.backup_location and os.path.exists(settings.backup_location):
                gdrive_dir = settings.backup_location
        finally:
            session.close()

        os.makedirs(hard_drive_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%p") # E.g. 2026-08-30_10-00-AM
        backup_filename = f"TailorShop_Backup_{timestamp}.zip"
        
        # Checkpoint the WAL before copying to ensure all data is in the .db file
        try:
            with get_engine().connect() as conn:
                conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
        except Exception as e:
            logger.warning(f"WAL Checkpoint failed: {e}")

        final_hd_path = os.path.join(hard_drive_dir, backup_filename)
        
        try:
            # 1. Clean up old backups first so we only keep 1 file
            for old_file in glob.glob(os.path.join(hard_drive_dir, "TailorShop_Backup_*.*")):
                try: os.remove(old_file)
                except: pass
                
            if gdrive_dir:
                for old_file in glob.glob(os.path.join(gdrive_dir, "TailorShop_Backup_*.*")):
                    try: os.remove(old_file)
                    except: pass
            
            # 2. Assemble new ZIP backup in temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                shutil.copy2(DATABASE_PATH, os.path.join(temp_dir, "tailor_shop.db"))
                if os.path.exists(UPLOADS_DIR):
                    shutil.copytree(UPLOADS_DIR, os.path.join(temp_dir, "uploads"))
                
                # Write to hard drive first
                with zipfile.ZipFile(final_hd_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
                            
            file_size = os.path.getsize(final_hd_path)
            
            # 3. Copy to Google Drive if available and different from hard drive dir
            if gdrive_dir and os.path.abspath(gdrive_dir) != os.path.abspath(hard_drive_dir):
                final_gdrive_path = os.path.join(gdrive_dir, backup_filename)
                shutil.copy2(final_hd_path, final_gdrive_path)

            # Log the backup
            session = get_session()
            try:
                settings_repo = SettingsRepository(session)
                settings_repo.add_backup_log(
                    backup_path=final_hd_path,
                    file_size=file_size,
                    status="SUCCESS",
                )
                session.commit()
            finally:
                session.close()

            logger.info(f"Backup created: {final_hd_path} ({file_size} bytes)")
            return final_hd_path

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            try:
                session = get_session()
                try:
                    settings_repo = SettingsRepository(session)
                    settings_repo.add_backup_log(
                        backup_path=final_hd_path,
                        file_size=0,
                        status="FAILED",
                    )
                    session.commit()
                finally:
                    session.close()
            except Exception:
                pass
            raise

    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore the database from a backup file (Supports both .db and .zip).
        IMPORTANT: This will replace the current database and uploads.
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        try:
            close_db()

            if backup_path.endswith('.zip'):
                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    extracted_db = os.path.join(temp_dir, "tailor_shop.db")
                    if os.path.exists(extracted_db):
                        shutil.copy2(extracted_db, DATABASE_PATH)
                    
                    extracted_uploads = os.path.join(temp_dir, "uploads")
                    if os.path.exists(extracted_uploads):
                        if os.path.exists(UPLOADS_DIR):
                            shutil.rmtree(UPLOADS_DIR)
                        shutil.copytree(extracted_uploads, UPLOADS_DIR)
            else:
                shutil.copy2(backup_path, DATABASE_PATH)

            init_db()
            logger.info(f"Database restored from: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise

    def get_backup_history(self) -> list:
        session = get_session()
        try:
            repo = SettingsRepository(session)
            return repo.get_backup_logs()
        finally:
            session.close()

    def get_last_backup_date(self) -> datetime | None:
        session = get_session()
        try:
            repo = SettingsRepository(session)
            last = repo.get_last_backup()
            return last.backup_date if last else None
        finally:
            session.close()

    def get_backup_location(self) -> str:
        session = get_session()
        try:
            repo = SettingsRepository(session)
            settings = repo.get_settings()
            return settings.backup_location or BACKUP_DEFAULT_DIR
        finally:
            session.close()
