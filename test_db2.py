from app.database.engine import init_db, get_session
from app.models.customer import Customer
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService
from sqlalchemy.orm import selectinload

init_db()

# emulate get_dashboard_stats
order_srv = OrderService()
dash_data = order_srv.get_dashboard_data()

# emulate create_customer
srv = CustomerService()
c = srv.create_customer(name="Test User 2", mobile="0987654321")

# emulate get_customers
session = get_session()
try:
    customers = session.query(Customer).options(selectinload(Customer.orders)).all()
    for c in customers:
        print(f"Customer {c.id}: {c.name}, in session: {c in session}")
        print(f"Orders count: {len(c.orders)}")
finally:
    session.close()
