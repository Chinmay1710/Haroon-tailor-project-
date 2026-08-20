from __future__ import annotations
"""Customer service — customer management."""

from app.database.engine import get_session
from app.repositories.customer_repo import CustomerRepository
from app.models.customer import Customer
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CustomerService:

    def create_customer(self, name: str, mobile: str = "",
                        address: str = "", notes: str = "") -> Customer:
        if not name or name.strip() == "":
            raise ValueError("Customer name cannot be empty")
        session = get_session()
        try:
            repo = CustomerRepository(session)
            customer = repo.create(name=name, mobile=mobile, address=address, notes=notes)
            session.commit()
            logger.info(f"Customer created: {customer.name} (ID: {customer.id})")
            return customer
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create customer: {e}")
            raise
        finally:
            session.close()

    def update_customer(self, customer_id: int, **kwargs) -> Customer | None:
        session = get_session()
        try:
            repo = CustomerRepository(session)
            customer = repo.update(customer_id, **kwargs)
            session.commit()
            return customer
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update customer: {e}")
            raise
        finally:
            session.close()

    def delete_customer(self, customer_id: int) -> bool:
        session = get_session()
        try:
            repo = CustomerRepository(session)
            result = repo.soft_delete(customer_id)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete customer: {e}")
            raise
        finally:
            session.close()

    def get_customer(self, customer_id: int) -> Customer | None:
        session = get_session()
        try:
            return CustomerRepository(session).get_by_id(customer_id)
        finally:
            session.close()

    def get_all_customers(self) -> list[Customer]:
        session = get_session()
        try:
            return CustomerRepository(session).get_all()
        finally:
            session.close()

    def search_customers(self, query: str) -> list[Customer]:
        session = get_session()
        try:
            return CustomerRepository(session).search(query)
        finally:
            session.close()
