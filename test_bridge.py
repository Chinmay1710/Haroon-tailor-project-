import sys
import os
import json
sys.path.append(os.getcwd())
from app.database.engine import init_db
from app.ui.web_bridge import WebBridge
from app.services.order_service import OrderService
from app.services.customer_service import CustomerService

init_db()
services = {
    "order": OrderService(),
    "customer": CustomerService()
}
bridge = WebBridge(services)
# Mock actionCompleted signal
class MockSignal:
    def emit(self, cb_id, response_str):
        if "error" in response_str:
            print("ERROR IN RESPONSE:", response_str)
        else:
            data = json.loads(response_str).get("data", [])
            print("Length of data array:", len(data))
            if data:
                print("First order ID:", data[0].get("id"))
                print("First order customer_name:", data[0].get("customer_name"))

bridge.actionCompleted = MockSignal()
# We bypass dispatch and call the logic directly to avoid thread issues
def run_action():
    action = "get_all_orders"
    order_srv = bridge.services["order"]
    orders = order_srv.get_all_orders()
    data = []
    for o in orders:
        data.append({
            "id": o.id,
            "order_number": o.order_number,
            "customer_name": o.customer.name if o.customer else "Unknown",
            "customer_id": o.customer.id if o.customer else None,
            "customer_mobile": o.customer.mobile if o.customer else "",
            "items": ", ".join([f"{i.quantity}x {i.clothing_type}" for i in o.items]) if o.items else "Custom",
            "image_path": o.items[0].image_path if o.items and o.items[0].image_path else "",
            "order_date": o.order_date.isoformat() if o.order_date else "",
            "delivery_date": o.delivery_date.isoformat() if o.delivery_date else "",
            "status": o.status,
            "total_amount": o.total_amount,
            "remaining_amount": o.remaining_amount,
            "updated_at": o.updated_at.isoformat() if hasattr(o, "updated_at") and o.updated_at else ""
        })
    data.sort(key=lambda x: x["updated_at"] if x.get("updated_at") else str(x["id"]), reverse=True)
    response = {"status": "success", "data": data}
    bridge.actionCompleted.emit("cb_1", json.dumps(response))

run_action()
