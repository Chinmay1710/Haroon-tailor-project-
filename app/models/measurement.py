from __future__ import annotations
"""Measurement models — profiles and individual measurement values."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.engine import Base


class MeasurementProfile(Base):
    __tablename__ = "measurement_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    template_type = Column(String(50), nullable=False)  # shirt, pant, kurta, blouse, suit, custom
    name = Column(String(200), nullable=False)           # e.g., "Rahul's Shirt"
    unit = Column(String(10), default="inches")          # inches or cm
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="measurement_profiles")
    values = relationship("MeasurementValue", back_populates="profile",
                          cascade="all, delete-orphan", order_by="MeasurementValue.display_order")

    def __repr__(self):
        return f"<MeasurementProfile(id={self.id}, name='{self.name}', type='{self.template_type}')>"


class MeasurementValue(Base):
    __tablename__ = "measurement_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("measurement_profiles.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    field_value = Column(String(50))
    display_order = Column(Integer, default=0)

    # Relationships
    profile = relationship("MeasurementProfile", back_populates="values")

    def __repr__(self):
        return f"<MeasurementValue(field='{self.field_name}', value='{self.field_value}')>"
