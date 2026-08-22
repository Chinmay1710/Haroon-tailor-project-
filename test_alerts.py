import sys, json
sys.path.insert(0, '.')
from datetime import date
from app.database.engine import init_db
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.measurement_service import MeasurementService
from app.services.expense_service import ExpenseService
from app.services.report_service import ReportService
from app.services.backup_service import BackupService
from app.services.worker_service import worker_service

init_db()

services = {
    'customer': CustomerService(),
    'order': OrderService(),
    'payment': PaymentService(),
    'measurement': MeasurementService(),
    'expense': ExpenseService(),
    'report': ReportService(),
    'backup': BackupService(),
    'worker': worker_service
}

# Simulate what web_bridge does for get_dashboard_stats
from datetime import datetime
order_srv = services["order"]
dash_data = order_srv.get_dashboard_data()

urgent_alerts = []
for o in dash_data.get("urgent_not_started", []):
    days_left = (o.delivery_date - date.today()).days
    urgent_alerts.append({
        "id": o.id,
        "order_number": o.order_number,
        "customer_name": o.customer.name if o.customer else "Unknown",
        "delivery_date": o.delivery_date.strftime("%d/%m/%Y") if o.delivery_date else "",
        "days_left": days_left,
        "items": ", ".join([item.clothing_type for item in o.items]) if o.items else "Various"
    })

print(f"\n=== urgent_alerts ({len(urgent_alerts)}): ===")
print(json.dumps(urgent_alerts, indent=2, ensure_ascii=False))

data = {
    "orders_today": dash_data["orders_today"],
    "sales_today": dash_data["today_sales"],
    "pending_payments": dash_data["pending_payments"],
    "deliveries_today": dash_data["deliveries_today"],
    "status_counts": dash_data["status_counts"],
    "urgent_alerts": urgent_alerts
}

full_response = {"status": "success", "data": data}
print(f"\n=== Full response urgent_alerts key present: {'urgent_alerts' in full_response['data']} ===")
print(f"=== urgent_alerts count: {len(full_response['data']['urgent_alerts'])} ===")
