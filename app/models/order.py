from __future__ import annotations
"""Order models — orders, order items, and measurement snapshots."""

from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Text, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.engine import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(20), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    status = Column(String(20), default="NEW", nullable=False, index=True)
    order_date = Column(Date, default=date.today, nullable=False)
    delivery_date = Column(Date, nullable=True)
    total_amount = Column(Float, default=0.0, nullable=False)
    advance_amount = Column(Float, default=0.0, nullable=False)
    paid_amount = Column(Float, default=0.0, nullable=False)
    special_instructions = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", order_by="Payment.payment_date", cascade="all, delete-orphan")

    @property
    def remaining_amount(self) -> float:
        """Calculate the remaining amount to be paid."""
        return max(0.0, self.total_amount - self.paid_amount)

    @property
    def payment_status(self) -> str:
        """Determine payment status based on amounts."""
        if self.paid_amount >= self.total_amount:
            return "PAID"
        elif self.paid_amount > 0:
            return "PARTIALLY PAID"
        return "UNPAID"

    @property
    def is_overdue(self) -> bool:
        """Check if the order is overdue."""
        if self.delivery_date and self.status not in ("DELIVERED", "CANCELLED"):
            return date.today() > self.delivery_date
        return False

    def __repr__(self):
        return f"<Order(id={self.id}, number='{self.order_number}', status='{self.status}')>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    clothing_type = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    notes = Column(Text)
    image_path = Column(String(255), nullable=True)

    # Relationships
    order = relationship("Order", back_populates="items")
    measurements = relationship("OrderMeasurement", back_populates="order_item",
                                cascade="all, delete-orphan",
                                order_by="OrderMeasurement.display_order")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, type='{self.clothing_type}', qty={self.quantity})>"


class OrderMeasurement(Base):
    """Immutable snapshot of measurements at order creation time."""
    __tablename__ = "order_measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    field_value = Column(String(50))
    unit = Column(String(10), default="inches")
    display_order = Column(Integer, default=0)

    # Relationships
    order_item = relationship("OrderItem", back_populates="measurements")

    def __repr__(self):
        return f"<OrderMeasurement(field='{self.field_name}', value='{self.field_value}')>"
