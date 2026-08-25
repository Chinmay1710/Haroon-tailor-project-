from __future__ import annotations
"""Report service — aggregated data for reports."""

from datetime import date, timedelta
from app.database.engine import get_session
from app.repositories.order_repo import OrderRepository
from app.repositories.payment_repo import PaymentRepository
from app.repositories.expense_repo import ExpenseRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReportService:

    def get_report_data(self, start_date: date, end_date: date) -> dict:
        """Get all report metrics for a date range."""
        session = get_session()
        try:
            order_repo = OrderRepository(session)
            pay_repo = PaymentRepository(session)
            expense_repo = ExpenseRepository(session)

            orders = order_repo.get_orders_in_date_range(start_date, end_date)
            total_sales = sum(o.total_amount for o in orders if o.status != "CANCELLED")
            total_orders = len([o for o in orders if o.status != "CANCELLED"])
            completed_orders = len([o for o in orders if o.status == "DELIVERED"])

            total_payments = pay_repo.get_total_in_range(start_date, end_date)
            pending_payments = pay_repo.get_total_pending()
            total_expenses = expense_repo.get_total_in_range(start_date, end_date)

            estimated_profit = total_payments - total_expenses

            return {
                "start_date": start_date,
                "end_date": end_date,
                "total_sales": total_sales,
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "total_payments": total_payments,
                "pending_payments": pending_payments,
                "total_expenses": total_expenses,
                "estimated_profit": estimated_profit,
                "orders": orders,
            }
        finally:
            session.close()

    def get_today_report(self) -> dict:
        today = date.today()
        return self.get_report_data(today, today)

    def get_this_week_report(self) -> dict:
        today = date.today()
        start = today - timedelta(days=today.weekday())
        return self.get_report_data(start, today)

    def get_this_month_report(self) -> dict:
        today = date.today()
        start = today.replace(day=1)
        return self.get_report_data(start, today)
