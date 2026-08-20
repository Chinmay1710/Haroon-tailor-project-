from __future__ import annotations
"""Expense model."""

from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, Date, Text, DateTime

from app.database.engine import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    expense_date = Column(Date, default=date.today, nullable=False)
    note = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Expense(id={self.id}, name='{self.name}', amount={self.amount})>"
