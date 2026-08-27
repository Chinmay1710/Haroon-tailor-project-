from __future__ import annotations
"""Stock models - Inventory tracking for tailor shop materials."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime

from app.database.engine import Base


class StockItem(Base):
    __tablename__ = "stock_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(50), nullable=False, default="Other")
    quantity = Column(Float, default=0.0, nullable=False)
    unit = Column(String(20), default="pieces", nullable=False)
    min_quantity = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<StockItem(id={self.id}, name='{self.name}', qty={self.quantity} {self.unit})>"
