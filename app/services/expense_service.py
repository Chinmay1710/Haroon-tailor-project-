from __future__ import annotations
"""Expense service — expense management."""

from datetime import date
from app.database.engine import get_session
from app.repositories.expense_repo import ExpenseRepository
from app.models.expense import Expense
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ExpenseService:

    def create_expense(self, name: str, category: str, amount: float,
                       expense_date: date = None, note: str = "") -> Expense:
        session = get_session()
        try:
            repo = ExpenseRepository(session)
            expense = repo.create(name=name, category=category, amount=amount,
                                  expense_date=expense_date, note=note)
            session.commit()
            logger.info(f"Expense created: {name} ({amount})")
            return expense
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create expense: {e}")
            raise
        finally:
            session.close()

    def update_expense(self, expense_id: int, **kwargs) -> Expense | None:
        session = get_session()
        try:
            repo = ExpenseRepository(session)
            expense = repo.update(expense_id, **kwargs)
            session.commit()
            return expense
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update expense: {e}")
            raise
        finally:
            session.close()

    def delete_expense(self, expense_id: int) -> bool:
        session = get_session()
        try:
            repo = ExpenseRepository(session)
            result = repo.delete(expense_id)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete expense: {e}")
            raise
        finally:
            session.close()

    def get_all_expenses(self) -> list[Expense]:
        session = get_session()
        try:
            return ExpenseRepository(session).get_all()
        finally:
            session.close()

    def get_expenses_in_range(self, start_date: date, end_date: date) -> list[Expense]:
        session = get_session()
        try:
            return ExpenseRepository(session).get_in_date_range(start_date, end_date)
        finally:
            session.close()

    def search_expenses(self, query: str) -> list[Expense]:
        session = get_session()
        try:
            return ExpenseRepository(session).search(query)
        finally:
            session.close()
