from __future__ import annotations
"""Settings repository — database operations for shop settings and backup logs."""

from sqlalchemy.orm import Session

from app.models.settings import ShopSettings, BackupLog


class SettingsRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_settings(self) -> ShopSettings:
        """Get or create the singleton settings row."""

        settings = self.session.query(ShopSettings).first()
        if not settings:
            settings = ShopSettings()
            self.session.add(settings)
            self.session.flush()
        return settings

    def update_settings(self, **kwargs) -> ShopSettings:
        settings = self.get_settings()
        for key, value in kwargs.items():
            if hasattr(settings, key) and key not in ("id", "created_at"):
                setattr(settings, key, value)
        self.session.flush()
        return settings

    def is_setup_done(self) -> bool:
        settings = self.get_settings()
        return settings.is_setup_done

    def mark_setup_done(self) -> ShopSettings:
        return self.update_settings(is_setup_done=True)

    # --- Backup Logs ---

    def add_backup_log(self, backup_path: str, file_size: int = 0,
                       status: str = "SUCCESS") -> BackupLog:
        log = BackupLog(
            backup_path=backup_path,
            file_size=file_size,
            status=status,
        )
        self.session.add(log)
        self.session.flush()
        return log

    def get_backup_logs(self, limit: int = 20) -> list[BackupLog]:
        return self.session.query(BackupLog).order_by(
            BackupLog.backup_date.desc()
        ).limit(limit).all()

    def get_last_backup(self) -> BackupLog | None:
        return self.session.query(BackupLog).filter(
            BackupLog.status == "SUCCESS"
        ).order_by(BackupLog.backup_date.desc()).first()
