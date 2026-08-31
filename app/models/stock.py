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
    unit_cost = Column(Float, default=0.0, nullable=False)  # Cost per unit for purchase tracking
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<StockItem(id={self.id}, name='{self.name}', qty={self.quantity} {self.unit})>"

class StockUsage(Base):
    __tablename__ = "stock_usage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(Integer, nullable=False, index=True) # Intentionally not using strict ForeignKey to avoid circular import loops if not needed, or we can use string "workers.id"
    stock_item_id = Column(Integer, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # We will fetch relationships dynamically or manually to avoid circular imports between worker.py and stock.py
    
    def __repr__(self):
        return f"<StockUsage(id={self.id}, worker_id={self.worker_id}, item_id={self.stock_item_id}, qty={self.quantity})>"
