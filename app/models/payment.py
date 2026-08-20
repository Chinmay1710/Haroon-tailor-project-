from __future__ import annotations
"""Payment model."""

from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.engine import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, default=date.today, nullable=False)
    payment_method = Column(String(20), default="Cash", nullable=False)
    note = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, method='{self.payment_method}')>"
