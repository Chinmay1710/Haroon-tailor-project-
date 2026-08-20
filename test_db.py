from app.database.engine import init_db, get_session
from app.models.customer import Customer
from app.services.customer_service import CustomerService
from sqlalchemy.orm import selectinload

init_db()

srv = CustomerService()
try:
    c = srv.create_customer(name="Test User", mobile="1234567890")
except Exception:
    pass

session = get_session()
try:
    customers = session.query(Customer).options(selectinload(Customer.orders)).all()
    for c in customers:
        print(f"Customer {c.id}: {c.name}, in session: {c in session}")
        print(f"Orders count: {len(c.orders)}")
finally:
    session.close()
