from __future__ import annotations
"""Backup service — SQLite file copy backup and restore."""

import os
import shutil
from datetime import datetime

from app.config import DATABASE_PATH, BACKUP_DEFAULT_DIR
from app.database.engine import get_session, close_db, init_db
from app.repositories.settings_repo import SettingsRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BackupService:

    def create_backup(self, backup_dir: str = None) -> str:
        """

        Create a backup copy of the SQLite database.
        Returns the path to the backup file.
        """
        backup_dir = backup_dir or BACKUP_DEFAULT_DIR
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_filename = f"TailorShop_Backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        try:
            shutil.copy2(DATABASE_PATH, backup_path)
            file_size = os.path.getsize(backup_path)

            # Log the backup
            session = get_session()
            try:
                settings_repo = SettingsRepository(session)
                settings_repo.add_backup_log(
                    backup_path=backup_path,
                    file_size=file_size,
                    status="SUCCESS",
                )
                session.commit()
            finally:
                session.close()

            logger.info(f"Backup created: {backup_path} ({file_size} bytes)")
            return backup_path

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            # Try to log the failure
            try:
                session = get_session()
                try:
                    settings_repo = SettingsRepository(session)
                    settings_repo.add_backup_log(
                        backup_path=backup_path,
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
        Restore the database from a backup file.
        IMPORTANT: This will replace the current database.
        The application should be restarted after restore.
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        try:
            # Close existing connections
            close_db()

            # Replace the active database
            shutil.copy2(backup_path, DATABASE_PATH)

            # Re-initialize
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
