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

from app.database.engine import get_session
from app.repositories.order_repo import OrderRepository
from app.services.order_service import OrderService

from app.ui.web_bridge import BackendBridge

bridge = BackendBridge(None, {"order": OrderService(OrderRepository(get_session()))})
print("Dispatching get_deliveries_dashboard...")
bridge.dispatch("get_deliveries_dashboard", "{}", lambda response: print("Response:", response))
