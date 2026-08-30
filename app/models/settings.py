from __future__ import annotations
"""Shop settings and backup log models."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime

from app.database.engine import Base
from app.config import (DEFAULT_CURRENCY, DEFAULT_MEASUREMENT_UNIT,
                        DEFAULT_DATE_FORMAT, DEFAULT_PAPER_SIZE, BACKUP_DEFAULT_DIR)


class ShopSettings(Base):
    __tablename__ = "shop_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_name = Column(String(200), default="My Tailor Shop")
    owner_name = Column(String(200), default="")
    phone = Column(String(20), default="")
    address = Column(Text, default="")
    currency = Column(String(10), default=DEFAULT_CURRENCY)
    measurement_unit = Column(String(10), default=DEFAULT_MEASUREMENT_UNIT)
    date_format = Column(String(20), default=DEFAULT_DATE_FORMAT)
    receipt_paper_size = Column(String(10), default=DEFAULT_PAPER_SIZE)
    backup_location = Column(Text, default=BACKUP_DEFAULT_DIR)
    auto_backup = Column(Boolean, default=True)
    is_setup_done = Column(Boolean, default=False)
    dictation_language = Column(String(20), default="en-IN")
    
    # Twilio Integration Settings
    twilio_account_sid = Column(String(255), default="")
    twilio_auth_token = Column(String(255), default="")
    twilio_sender_number = Column(String(20), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<ShopSettings(shop='{self.shop_name}', setup_done={self.is_setup_done})>"


class BackupLog(Base):
    __tablename__ = "backup_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    backup_path = Column(Text, nullable=False)
    backup_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    file_size = Column(Integer)
    status = Column(String(20), default="SUCCESS")

    def __repr__(self):
        return f"<BackupLog(id={self.id}, date='{self.backup_date}', status='{self.status}')>"
