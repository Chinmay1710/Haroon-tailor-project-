import sys
import os

sys.path.append(os.path.abspath("."))
import app.models.customer
import app.models.measurement
import app.models.order
import app.models.payment
import app.models.expense
import app.models.settings
import app.models.worker

from app.services.order_service import OrderService
order_srv = OrderService()

from datetime import date, timedelta
today = date.today()
tomorrow = today + timedelta(days=1)

orders = order_srv.get_all_orders()
deliveries = []
counts = {"due_today": 0, "due_tomorrow": 0, "upcoming": 0, "overdue": 0}

for o in orders:
    if o.status != "READY": continue
    if o.delivery_date:
        if o.delivery_date < today: counts["overdue"] += 1
        elif o.delivery_date == today: counts["due_today"] += 1
        elif o.delivery_date == tomorrow: counts["due_tomorrow"] += 1
        else: counts["upcoming"] += 1
    
    deliveries.append({
        "id": o.id,
        "order_number": o.order_number,
        "customer_name": o.customer.name if o.customer else "",
        "mobile": o.customer.mobile if o.customer else "",
        "items": "Various",
        "delivery_date": o.delivery_date.isoformat() if o.delivery_date else "",
        "status": o.status,
        "total_amount": o.total_amount,
        "advance_paid": o.advance_paid
    })

print("Deliveries:", deliveries)
