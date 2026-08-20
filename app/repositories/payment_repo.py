from __future__ import annotations
"""Payment repository — database operations for payments."""

from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.payment import Payment


class PaymentRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(self, order_id: int, customer_id: int, amount: float,
               payment_date: date = None, payment_method: str = "Cash",
               note: str = "") -> Payment:
        payment = Payment(
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            payment_date=payment_date or date.today(),
            payment_method=payment_method,
            note=note,
        )
        self.session.add(payment)
        self.session.flush()
        return payment

    def get_by_id(self, payment_id: int) -> Payment | None:
        return self.session.query(Payment).options(
            joinedload(Payment.order),
            joinedload(Payment.customer),
        ).filter(Payment.id == payment_id).first()

    def get_all(self) -> list[Payment]:
        return self.session.query(Payment).options(
            joinedload(Payment.order),
            joinedload(Payment.customer),
        ).order_by(Payment.payment_date.desc()).all()

    def get_by_order(self, order_id: int) -> list[Payment]:
        return self.session.query(Payment).filter(
            Payment.order_id == order_id
        ).order_by(Payment.payment_date).all()

    def get_by_customer(self, customer_id: int) -> list[Payment]:
        return self.session.query(Payment).options(
            joinedload(Payment.order),
        ).filter(
            Payment.customer_id == customer_id
        ).order_by(Payment.payment_date.desc()).all()

    def get_in_date_range(self, start_date: date, end_date: date) -> list[Payment]:
        return self.session.query(Payment).options(
            joinedload(Payment.order),
            joinedload(Payment.customer),
        ).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date,
        ).order_by(Payment.payment_date.desc()).all()

    def get_today_total(self) -> float:
        result = self.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date == date.today()
        ).scalar()
        return result or 0.0

    def get_total_in_range(self, start_date: date, end_date: date) -> float:
        result = self.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date,
        ).scalar()
        return result or 0.0

    def get_total_pending(self) -> float:
        """Get total remaining payments across all non-cancelled orders."""

        from app.models.order import Order
        results = self.session.query(
            func.sum(Order.total_amount - Order.paid_amount)
        ).filter(
            Order.status.notin_(["CANCELLED"]),
            Order.total_amount > Order.paid_amount,
        ).scalar()
        return results or 0.0
