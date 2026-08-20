from __future__ import annotations
"""Expense repository — database operations for expenses."""

from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.expense import Expense


class ExpenseRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, category: str, amount: float,
               expense_date: date = None, note: str = "") -> Expense:
        expense = Expense(
            name=name,
            category=category,
            amount=amount,
            expense_date=expense_date or date.today(),
            note=note,
        )
        self.session.add(expense)
        self.session.flush()
        return expense

    def get_by_id(self, expense_id: int) -> Expense | None:
        return self.session.query(Expense).filter(Expense.id == expense_id).first()

    def get_all(self) -> list[Expense]:
        return self.session.query(Expense).order_by(Expense.expense_date.desc()).all()

    def get_in_date_range(self, start_date: date, end_date: date) -> list[Expense]:
        return self.session.query(Expense).filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
        ).order_by(Expense.expense_date.desc()).all()

    def search(self, query: str) -> list[Expense]:
        q = f"%{query}%"
        return self.session.query(Expense).filter(
            Expense.name.ilike(q)
        ).order_by(Expense.expense_date.desc()).all()

    def update(self, expense_id: int, **kwargs) -> Expense | None:
        expense = self.get_by_id(expense_id)
        if expense:
            for key, value in kwargs.items():
                if hasattr(expense, key) and key not in ("id", "created_at"):
                    setattr(expense, key, value)
            self.session.flush()
        return expense

    def delete(self, expense_id: int) -> bool:
        expense = self.get_by_id(expense_id)
        if expense:
            self.session.delete(expense)
            self.session.flush()
            return True
        return False

    def get_total_in_range(self, start_date: date, end_date: date) -> float:
        result = self.session.query(func.sum(Expense.amount)).filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
        ).scalar()
        return result or 0.0
