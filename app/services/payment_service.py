from __future__ import annotations
"""Payment service — payment processing with validation."""

from datetime import date
from app.database.engine import get_session
from app.repositories.payment_repo import PaymentRepository
from app.repositories.order_repo import OrderRepository
from app.models.payment import Payment
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PaymentService:

    def add_payment(self, order_id: int, amount: float,
                    payment_date: date = None, payment_method: str = "Cash",
                    note: str = "") -> Payment:
        """

        Add a payment to an order with validation.
        Raises ValueError if amount exceeds remaining balance.
        """
        session = get_session()
        try:
            order_repo = OrderRepository(session)
            order = order_repo.get_by_id(order_id)
            if not order:
                raise ValueError("Order not found")

            remaining = order.remaining_amount
            if amount <= 0:
                raise ValueError("Payment amount must be greater than 0")
            if amount > remaining + 0.01:  # small tolerance for float precision
                raise ValueError(
                    f"Payment amount (₹{amount:.2f}) exceeds remaining balance (₹{remaining:.2f})"
                )

            pay_repo = PaymentRepository(session)
            payment = pay_repo.create(
                order_id=order_id,
                customer_id=order.customer_id,
                amount=amount,
                payment_date=payment_date or date.today(),
                payment_method=payment_method,
                note=note,
            )

            # Update order's paid amount
            order.paid_amount = (order.paid_amount or 0) + amount
            session.flush()

            session.commit()
            logger.info(f"Payment of {amount} added to order {order.order_number}")
            return payment
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add payment: {e}")
            raise
        finally:
            session.close()

    def delete_payment(self, payment_id: int):
        session = get_session()
        try:
            pay_repo = PaymentRepository(session)
            payment = pay_repo.get_by_id(payment_id)
            if not payment:
                return
            
            # Revert order's paid amount
            order_repo = OrderRepository(session)
            order = order_repo.get_by_id(payment.order_id)
            if order:
                order.paid_amount = (order.paid_amount or 0) - payment.amount
            
            session.delete(payment)
            session.commit()
            logger.info(f"Payment {payment_id} deleted and order updated.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete payment: {e}")
        finally:
            session.close()

    def get_all_payments(self) -> list[Payment]:
        session = get_session()
        try:
            return PaymentRepository(session).get_all()
        finally:
            session.close()

    def get_payments_for_order(self, order_id: int) -> list[Payment]:
        session = get_session()
        try:
            return PaymentRepository(session).get_by_order(order_id)
        finally:
            session.close()

    def get_payments_in_range(self, start_date: date, end_date: date) -> list[Payment]:
        session = get_session()
        try:
            return PaymentRepository(session).get_in_date_range(start_date, end_date)
        finally:
            session.close()

    def get_today_total(self) -> float:
        session = get_session()
        try:
            return PaymentRepository(session).get_today_total()
        finally:
            session.close()
