import json
from app.ui.web_bridge import WebBridge

def get_services():
    from app.services.order_service import OrderService
    from app.services.measurement_service import MeasurementService
    from app.services.payment_service import PaymentService
    return {
        "order": OrderService(),
        "measurement": MeasurementService(),
        "payment": PaymentService(),
    }

bridge = WebBridge(get_services())
print(bridge.dispatch('get_dashboard_stats', '{}'))
