import sys
import os

# Add the project root to python path so we can import app modules
sys.path.append(os.path.abspath("."))

from app.database.engine import get_session
from app.repositories.order_repo import OrderRepository

session = get_session()
repo = OrderRepository(session)
orders = repo.get_all()

ready_orders = [o for o in orders if o.status == "READY"]
print("Total Ready Orders:", len(ready_orders))
for o in ready_orders:
    print(o.id, o.order_number, o.status, o.total_amount, o.advance_paid, type(o.delivery_date))

session.close()
