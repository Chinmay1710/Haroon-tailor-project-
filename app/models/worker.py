from __future__ import annotations
"""Worker models - workers and assigned tasks."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database.engine import Base

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    pin = Column(String(4), nullable=False) # 4-digit PIN for portal login
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    tasks = relationship("WorkerTask", back_populates="worker", cascade="all, delete-orphan")


class WorkerTask(Base):
    __tablename__ = "worker_tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False, index=True)
    
    # Piece-rate amount for this specific task
    payout_amount = Column(Float, default=0.0, nullable=False)
    
    status = Column(String(20), default="ASSIGNED", nullable=False) # ASSIGNED, COMPLETED, PAID
    
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    worker = relationship("Worker", back_populates="tasks")
    order_item = relationship("OrderItem", backref="worker_tasks")
