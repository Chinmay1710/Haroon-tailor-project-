import time
import os
import psutil
from datetime import date, timedelta
import random

from app.database.engine import init_db, get_session, get_engine
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.ui.web_bridge import WebBridge
from sqlalchemy import text

print("--- 1. Verification of SQLite PRAGMAs ---")
init_db()
with get_engine().connect() as conn:
    jm = conn.execute(text("PRAGMA journal_mode")).scalar()
    sync = conn.execute(text("PRAGMA synchronous")).scalar()
    print(f"Journal Mode: {jm} (WAL is required for synchronous=NORMAL safety)")
    print(f"Synchronous: {sync} (1 means NORMAL)")

print("\n--- 2. Populating Large Realistic Dataset ---")
session = get_session()

existing_cust = session.query(Customer).count()
if existing_cust < 500:
    print("Generating 1000 customers, 5000 orders, 10000 payments... (this might take a few seconds)")
    customers = []
    for i in range(1000):
        c = Customer(name=f"Test Customer {i}", mobile=f"+9198765{i:05d}")
        customers.append(c)
    session.add_all(customers)
    session.flush()

    orders = []
    for i in range(5000):
        c_id = random.choice(customers).id
        order_date = date.today() - timedelta(days=random.randint(0, 365))
        delivery_date = order_date + timedelta(days=7)
        o = Order(
            order_number=f"B-ORD-{i:06d}",
            customer_id=c_id,
            status=random.choice(["NEW", "STITCHING_COMPLETE", "DELIVERED"]),
            order_date=order_date,
            delivery_date=delivery_date,
            total_amount=1500.0,
            paid_amount=500.0
        )
        orders.append(o)
    session.add_all(orders)
    session.flush()

    payments = []
    for o in orders:
        payments.append(Payment(
            order_id=o.id,
            customer_id=o.customer_id,
            amount=500.0,
            payment_date=o.order_date
        ))
    session.add_all(payments)
    session.commit()
    print("Data generated!")
else:
    print(f"Database already has {existing_cust} customers, skipping generation.")

print(f"DB Sizes - Customers: {session.query(Customer).count()}, Orders: {session.query(Order).count()}, Payments: {session.query(Payment).count()}")
session.close()

print("\n--- 3. Measuring Loading Times (Main Thread Blocking Time) ---")
class DummyBridge(WebBridge):
    def __init__(self):
        # Provide dummy services dict as required by web_bridge init
        from app.services.order_service import OrderService
        from app.services.worker_service import WorkerService
        self.services = {
            "order": OrderService(),
            "worker": WorkerService()
        }
        super().__init__(self.services)
        
bridge = DummyBridge()
process = psutil.Process(os.getpid())

def measure(action, payload="{}"):
    t0 = time.time()
    bridge.dispatch(action, payload)
    t1 = time.time()
    mem = process.memory_info().rss / (1024 * 1024)
    cpu = process.cpu_percent(interval=None)
    print(f"Action '{action}' took {(t1-t0)*1000:.2f} ms | Mem: {mem:.2f} MB | CPU: {cpu:.1f}%")

# Warm up psutil cpu percent
process.cpu_percent(interval=None)

measure("get_dashboard_stats")
measure("get_customers")
measure("get_orders")
measure("get_payments_dashboard")
measure("get_deliveries_dashboard")

print("\n--- 4. Cache & Session Consistency ---")
bridge._settings_cache = None
t0 = time.time()
bridge.dispatch("get_settings", "{}")
t1 = time.time()
print(f"get_settings (DB Miss) took {(t1-t0)*1000:.2f} ms")

t0 = time.time()
bridge.dispatch("get_settings", "{}")
t1 = time.time()
print(f"get_settings (Cache Hit) took {(t1-t0)*1000:.2f} ms")

print("\nVerification Complete.")
