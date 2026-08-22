from __future__ import annotations
"""Worker models - workers and assigned tasks."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

from app.database.engine import Base

class WorkerType(str, enum.Enum):
    DAILY_SALARY = "DAILY_SALARY"
    PIECE_RATE = "PIECE_RATE"

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    pin = Column(String(4), nullable=False) # 4-digit PIN for portal login
    worker_type = Column(String(20), default=WorkerType.PIECE_RATE.value, nullable=False)
    daily_rate = Column(Float, default=0.0, nullable=False) # Only for DAILY_SALARY workers
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    tasks = relationship("WorkerTask", back_populates="worker", cascade="all, delete-orphan")
    advances = relationship("WorkerAdvance", back_populates="worker", cascade="all, delete-orphan")
    work_entries = relationship("WorkEntry", back_populates="worker", cascade="all, delete-orphan")


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


class GarmentRate(Base):
    __tablename__ = "garment_rates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    garment_type = Column(String(100), nullable=False, unique=True)
    rate = Column(Float, default=0.0, nullable=False)


class WorkEntry(Base):
    __tablename__ = "work_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    
    entry_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    garment_type = Column(String(100), nullable=True)
    quantity = Column(Integer, default=0, nullable=False)
    bill_number = Column(String(100), nullable=True)
    
    extra_work_description = Column(String(255), nullable=True)
    extra_amount = Column(Float, default=0.0, nullable=False)
    
    total_amount = Column(Float, default=0.0, nullable=False)
    
    status = Column(String(20), default="PENDING", nullable=False) # PENDING, APPROVED, REJECTED
    
    worker = relationship("Worker", back_populates="work_entries")


class WorkerAdvance(Base):
    __tablename__ = "worker_advances"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    
    amount = Column(Float, default=0.0, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    notes = Column(String(255), nullable=True)
    
    worker = relationship("Worker", back_populates="advances")
