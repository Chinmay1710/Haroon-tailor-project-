from __future__ import annotations
"""Customer repository — database operations for customers."""

from sqlalchemy import or_, String
from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, mobile: str = "", address: str = "", notes: str = "") -> Customer:
        customer = Customer(name=name, mobile=mobile, address=address, notes=notes)
        self.session.add(customer)
        self.session.flush()
        return customer

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.session.query(Customer).filter(
            Customer.id == customer_id, Customer.is_active == True  # noqa: E712
        ).first()

    def get_all(self, limit: int = None, offset: int = 0) -> list[Customer]:
        return self.session.query(Customer).filter(
            Customer.is_active == True  # noqa: E712
        ).order_by(Customer.name).limit(limit).offset(offset).all()

    def count_all(self) -> int:
        return self.session.query(Customer).filter(
            Customer.is_active == True  # noqa: E712
        ).count()

    def search(self, query: str, limit: int = None, offset: int = 0) -> list[Customer]:
        q = f"%{query}%"
        return self.session.query(Customer).filter(
            Customer.is_active == True,  # noqa: E712
            or_(
                Customer.name.ilike(q),
                Customer.mobile.ilike(q),
                Customer.id.cast(String).ilike(q),
            )
        ).order_by(Customer.name).limit(limit).offset(offset).all()

    def count_search(self, query: str) -> int:
        q = f"%{query}%"
        return self.session.query(Customer).filter(
            Customer.is_active == True,  # noqa: E712
            or_(
                Customer.name.ilike(q),
                Customer.mobile.ilike(q),
                Customer.id.cast(String).ilike(q),
            )
        ).count()

    def update(self, customer_id: int, **kwargs) -> Customer | None:
        customer = self.get_by_id(customer_id)
        if customer:
            for key, value in kwargs.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            self.session.flush()
        return customer

    def soft_delete(self, customer_id: int) -> bool:
        customer = self.get_by_id(customer_id)
        if customer:
            customer.is_active = False
            self.session.flush()
            return True
        return False

    def count(self) -> int:
        return self.session.query(Customer).filter(
            Customer.is_active == True  # noqa: E712
        ).count()
