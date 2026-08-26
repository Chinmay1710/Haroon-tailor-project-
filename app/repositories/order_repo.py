from __future__ import annotations
"""Order repository — database operations for orders."""

from datetime import date, timedelta
from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload

from app.models.order import Order, OrderItem, OrderMeasurement
from app.config import ORDER_NUMBER_PREFIX, ORDER_NUMBER_FORMAT


class OrderRepository:

    def __init__(self, session: Session):
        self.session = session

    def _generate_order_number(self) -> str:
        """Generate the next sequential order number."""

        last = self.session.query(func.max(Order.id)).scalar() or 0
        return ORDER_NUMBER_FORMAT.format(prefix=ORDER_NUMBER_PREFIX, seq=last + 1)

    def create(self, customer_id: int, order_date: date = None,
               delivery_date: date = None, total_amount: float = 0.0,
               advance_amount: float = 0.0, special_instructions: str = "",
               notes: str = "") -> Order:
        order = Order(
            order_number=self._generate_order_number(),
            customer_id=customer_id,
            status="NEW",
            order_date=order_date or date.today(),
            delivery_date=delivery_date,
            total_amount=total_amount,
            advance_amount=advance_amount,
            paid_amount=advance_amount,  # advance is initial payment
            special_instructions=special_instructions,
            notes=notes,
        )
        self.session.add(order)
        self.session.flush()
        return order

    def clear_items(self, order_id: int):
        """Delete all existing items (and cascade their measurements) for an order."""
        items = self.session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        for item in items:
            self.session.delete(item)
        self.session.flush()

    def add_item(self, order_id: int, clothing_type: str,
                 quantity: int = 1, price: float = 0.0, notes: str = "", image_path: str = None) -> OrderItem:
        item = OrderItem(
            order_id=order_id,
            clothing_type=clothing_type,
            quantity=quantity,
            price=price,
            notes=notes,
            image_path=image_path
        )
        self.session.add(item)
        self.session.flush()
        return item

    def add_measurement_snapshot(self, order_item_id: int, field_name: str,
                                 field_value: str, unit: str = "inches",
                                 display_order: int = 0) -> OrderMeasurement:
        """Add a measurement snapshot (immutable copy) to an order item."""
        measurement = OrderMeasurement(
            order_item_id=order_item_id,
            field_name=field_name,
            field_value=field_value,
            unit=unit,
            display_order=display_order,
        )
        self.session.add(measurement)
        self.session.flush()
        return measurement

    def get_by_id(self, order_id: int) -> Order | None:
        return self.session.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.items).joinedload(OrderItem.measurements),
            joinedload(Order.payments),
        ).filter(Order.id == order_id).first()

    def get_by_order_number(self, order_number: str) -> Order | None:
        return self.session.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.items).joinedload(OrderItem.measurements),
            joinedload(Order.payments),
        ).filter(Order.order_number == order_number).first()

    def get_all(self, status: str = None) -> list[Order]:
        query = self.session.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.items),
        )
        if status:
            query = query.filter(Order.status == status)
        return query.order_by(Order.created_at.desc()).all()

    def get_overdue(self) -> list[Order]:
        today = date.today()
        return self.session.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.items),
        ).filter(
            Order.delivery_date < today,
            Order.status.notin_(["DELIVERED", "CANCELLED"]),
        ).order_by(Order.delivery_date).all()

    def get_by_delivery_date(self, target_date: date) -> list[Order]:
        return self.session.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.items),
        ).filter(
            Order.delivery_date == target_date,
            Order.status.notin_(["CANCELLED"]),
        ).order_by(Order.order_number).all()

    def get_upcoming_deliveries(self, days: int = 7) -> list[Order]:
        today = date.today()
        future = today + timedelta(days=days)
        return self.session.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.items),
        ).filter(
            Order.delivery_date > today,
            Order.delivery_date <= future,
            Order.status.notin_(["DELIVERED", "CANCELLED"]),
        ).order_by(Order.delivery_date).all()

    def get_urgent_not_started(self, warning_days: int = 3) -> list[Order]:
        """Get orders whose delivery is within `warning_days` but work hasn't started (status=NEW)."""
        today = date.today()
        deadline = today + timedelta(days=warning_days)
        return self.session.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.items),
        ).filter(
            Order.delivery_date <= deadline,
            Order.delivery_date >= today,
            Order.status == "NEW",
        ).order_by(Order.delivery_date).all()

    def get_by_customer(self, customer_id: int) -> list[Order]:
        return self.session.query(Order).options(
            joinedload(Order.items),
        ).filter(
            Order.customer_id == customer_id
        ).order_by(Order.created_at.desc()).all()

    def search(self, query: str) -> list[Order]:
        q = f"%{query}%"
        return self.session.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.items),
        ).filter(
            or_(
                Order.order_number.ilike(q),
                Order.customer.has(name=query),
            )
        ).order_by(Order.created_at.desc()).all()

    def update_status(self, order_id: int, status: str) -> Order | None:
        order = self.session.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status
            self.session.flush()
        return order

    def update(self, order_id: int, **kwargs) -> Order | None:
        order = self.session.query(Order).filter(Order.id == order_id).first()
        if order:
            for key, value in kwargs.items():
                if hasattr(order, key) and key not in ("id", "order_number", "created_at"):
                    setattr(order, key, value)
            self.session.flush()
        return order

    def count_by_status(self) -> dict[str, int]:
        """Return a count of orders per status."""
        results = self.session.query(
            Order.status, func.count(Order.id)
        ).group_by(Order.status).all()
        counts = {status: 0 for status in ["NEW", "CUTTING_COMPLETE", "STITCHING_COMPLETE", "DELIVERED", "CANCELLED"]}
        for status, count in results:
            counts[status] = count
        # Add overdue count
        counts["OVERDUE"] = len(self.get_overdue())
        return counts

    def get_today_orders(self, target_date: date = None) -> list[Order]:
        target_date = target_date or date.today()
        return self.session.query(Order).options(
            joinedload(Order.customer),
        ).filter(
            Order.order_date == target_date
        ).order_by(Order.created_at.desc()).all()

    def get_recent(self, limit: int = 5) -> list[Order]:
        return self.session.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.items),
        ).order_by(Order.created_at.desc()).limit(limit).all()

    def get_orders_in_date_range(self, start_date: date, end_date: date) -> list[Order]:
        return self.session.query(Order).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date,
        ).all()
