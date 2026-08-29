import os
import uvicorn
import logging
from threading import Thread
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.worker_service import worker_service
from app.config import ASSETS_DIR

logger = logging.getLogger(__name__)

# Global reference to the WebBridge for signaling the UI thread
bridge_instance = None

app = FastAPI(title="Haroon Tailor Worker Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# We will serve mobile web assets from app/assets/mobile
mobile_assets_dir = os.path.join(ASSETS_DIR, "mobile")
os.makedirs(mobile_assets_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=mobile_assets_dir), name="static")

from app.config import APP_DATA_DIR
receipts_dir = os.path.join(APP_DATA_DIR, "receipts")
os.makedirs(receipts_dir, exist_ok=True)
app.mount("/receipts", StaticFiles(directory=receipts_dir), name="receipts")

class LoginRequest(BaseModel):
    name: str
    pin: str

class CustomerRequest(BaseModel):
    name: str
    mobile: str = ""
    address: str = ""

class MobileOrderRequest(BaseModel):
    customer_id: int
    garment_type: str
    quantity: int
    price: float
    measurements_text: str = ""
    special_instructions: str = ""
    advance_amount: float = 0.0
    save_profile: bool = False
    image_base64: Optional[List[str]] = None


@app.post("/api/login")
def login(req: LoginRequest):
    worker = worker_service.authenticate_worker(req.name, req.pin)
    if not worker:
        raise HTTPException(status_code=401, detail="Invalid name or PIN")
    return {"status": "success", "worker": worker}

@app.post("/api/customers/add")
def add_customer(req: CustomerRequest):
    from app.services.customer_service import CustomerService
    try:
        cust_srv = CustomerService()
        customer = cust_srv.create_customer(name=req.name, mobile=req.mobile, address=req.address)
        if bridge_instance:
            bridge_instance.notification_requested.emit("Success", f"New Customer Added: {customer.name}")
            if hasattr(bridge_instance, "customer_added"):
                bridge_instance.customer_added.emit()
        return {"status": "success", "customer_id": customer.id}
    except Exception as e:
        logger.error(f"Failed to add customer via API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/customers")
def search_customers(q: str = ""):
    from app.services.customer_service import CustomerService
    cust_srv = CustomerService()
    customers = cust_srv.search_customers(q)
    return {
        "status": "success",
        "customers": [{"id": c.id, "name": c.name, "mobile": c.mobile} for c in customers]
    }

@app.post("/api/orders/create")
def create_mobile_order(req: MobileOrderRequest):
    from app.services.order_service import OrderService
    from datetime import date
    try:
        srv = OrderService()
        items = [{
            "clothing_type": req.garment_type,
            "quantity": req.quantity,
            "price": req.price,
            "notes": "Measurements: " + req.measurements_text if req.measurements_text else ""
        }]
        
        order = srv.create_order(
            customer_id=req.customer_id,
            items=items,
            order_date=date.today(),
            delivery_date=None,
            special_instructions=req.special_instructions,
            advance_amount=req.advance_amount
        )
        
        if bridge_instance:
            bridge_instance.notification_requested.emit("Success", f"New Order Added: {order.order_number}")
            if hasattr(bridge_instance, "order_updated"):
                bridge_instance.order_updated.emit()
                
        return {"status": "success", "order_id": order.id, "order_number": order.order_number}
    except Exception as e:
        logger.error(f"Failed to create order via API: {e}")
        raise HTTPException(status_code=400, detail=str(e))



class WorkEntryRequest(BaseModel):
    garment_type: Optional[str] = None
    quantity: int = 0
    bill_number: Optional[str] = None
    extra_work_description: Optional[str] = None
    extra_amount: float = 0.0
    stock_item_id: Optional[int] = None
    stock_quantity: float = 0.0

@app.post("/api/worker/{worker_id}/work-entry")
def submit_work_entry(worker_id: int, req: WorkEntryRequest):
    res = worker_service.submit_work_entry(
        worker_id=worker_id,
        garment_type=req.garment_type,
        quantity=req.quantity,
        bill_number=req.bill_number,
        extra_work_description=req.extra_work_description,
        extra_amount=req.extra_amount
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
        
    if req.stock_item_id and req.stock_quantity > 0:
        from app.services.stock_service import stock_service
        try:
            stock_service.adjust_stock(req.stock_item_id, req.stock_quantity, "consume", worker_id)
        except Exception as e:
            logger.error(f"Failed to record stock usage: {e}")
            
    return {"status": "success", "entry": res}

class WorkerAdvanceRequest(BaseModel):
    order_id: int
    amount: float
    payment_method: str = "Cash"
    note: str = ""

@app.post("/api/worker/{worker_id}/advance")
def submit_worker_advance(worker_id: int, req: WorkerAdvanceRequest):
    notes = f"Order {req.order_id} ({req.payment_method})"
    if req.note:
        notes += f" - {req.note}"
    try:
        advance = worker_service.record_advance(worker_id, req.amount, notes)
        return {"status": "success", "advance": advance}
    except Exception as e:
        logger.error(f"Failed to record worker advance: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/worker/{worker_id}/entries")
def get_worker_entries(worker_id: int):
    entries = worker_service.get_worker_entries(worker_id)
    return {"status": "success", "entries": entries}

@app.get("/api/worker/{worker_id}/ledger")
def get_worker_ledger(worker_id: int):
    ledger = worker_service.get_worker_ledger(worker_id)
    return {"status": "success", "ledger": ledger}

@app.get("/api/garment-rates")
def get_garment_rates():
    rates = worker_service.get_garment_rates()
    return {"status": "success", "rates": rates}

@app.get("/api/stock-items")
def get_stock_items():
    from app.services.stock_service import stock_service
    items = stock_service.get_all_stock()
    return {
        "status": "success",
        "items": [{"id": i.id, "name": i.name, "unit": i.unit, "quantity": i.quantity} for i in items]
    }
@app.get("/api/orders/{order_id}")
def get_order_details(order_id: int):
    from app.services.order_service import OrderService
    srv = OrderService()
    order = srv.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items = []
    for item in order.items:
        items.append({"clothing_type": item.clothing_type, "quantity": item.quantity})
        
    return {
        "status": "success", 
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "customer_name": order.customer.name if order.customer else "Unknown",
            "customer_mobile": order.customer.mobile if order.customer else "",
            "customer_address": order.customer.address if order.customer else "",
            "status": order.status,
            "total_amount": order.total_amount,
            "paid_amount": order.paid_amount,
            "remaining_amount": order.remaining_amount,
            "items": items
        }
    }

class PaymentRequest(BaseModel):
    pin: str
    amount: float
    payment_method: str = "Cash"
    note: str = ""

@app.post("/api/orders/{order_id}/payment")
def submit_order_payment(order_id: int, req: PaymentRequest):
    # 1. Verify PIN by checking all workers (same as stage update)
    workers = worker_service.get_all_workers()
    matched_worker = None
    for w in workers:
        if w["pin"] == req.pin and w["is_active"]:
            matched_worker = w
            break
            
    if not matched_worker:
        raise HTTPException(status_code=401, detail="Invalid PIN")
        
    # 2. Add the payment
    from app.services.payment_service import PaymentService
    srv = PaymentService()
    try:
        payment = srv.add_payment(
            order_id=order_id,
            amount=req.amount,
            payment_method=req.payment_method,
            note=f"Collected by {matched_worker['name']} (Mobile) - {req.note}"
        )
        
        if bridge_instance:
            bridge_instance.notification_requested.emit("Success", f"Payment of ₹{req.amount} collected for Order {order_id}")
            if hasattr(bridge_instance, "order_updated"):
                bridge_instance.order_updated.emit()
            if hasattr(bridge_instance, "dashboard_updated"):
                bridge_instance.dashboard_updated.emit()
                
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to add mobile payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


class StageRequest(BaseModel):
    pin: str
    stage: str
    extra_amount: float = 0.0
    extra_desc: str = ""

@app.post("/api/orders/{order_id}/stage")
def submit_order_stage(order_id: int, req: StageRequest):
    # 1. Verify PIN by checking all workers
    workers = worker_service.get_all_workers()
    matched_worker = None
    for w in workers:
        if w["pin"] == req.pin and w["is_active"]:
            matched_worker = w
            break
            
    if not matched_worker:
        raise HTTPException(status_code=401, detail="Invalid PIN")
        
    # 2. Update the order
    from app.services.order_service import OrderService
    srv = OrderService()
    try:
        srv.mark_stage_complete(
            order_id=order_id,
            stage_name=req.stage,
            worker_id=matched_worker["id"],
            extra_amount=req.extra_amount,
            extra_desc=req.extra_desc
        )
        
        if bridge_instance:
            bridge_instance.notification_requested.emit("Info", f"Order {order_id} status updated to {req.stage.replace('_', ' ')}")
            if hasattr(bridge_instance, "order_added"):
                bridge_instance.order_added.emit()
                
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class MobileOrderRequest(BaseModel):
    customer_id: int
    garment_type: str
    quantity: int
    price: float
    measurements_text: str = ""
    special_instructions: str = ""
    advance_amount: float = 0.0
    save_profile: bool = False
    image_base64: Optional[List[str]] = None

@app.post("/api/orders/create")
def create_mobile_order(req: MobileOrderRequest):
    logger.info(f"Creating new order from worker portal for customer: {req.customer_id}")
    try:
        from app.services.order_service import OrderService
        from datetime import date
        
        srv = OrderService()
        
        # Try to parse measurements_text into a dictionary
        measurements_dict = {}
        if req.measurements_text:
            # simple parsing: comma or newline separated "key: value"
            import re
            parts = re.split(r'[,\n]', req.measurements_text)
            for part in parts:
                if ':' in part:
                    k, v = part.split(':', 1)
                    measurements_dict[k.strip()] = v.strip()
                elif part.strip():
                    measurements_dict[part.strip()] = ""
                    
        item_data = {
            "clothing_type": req.garment_type,
            "quantity": req.quantity,
            "price": req.price,
            "measurements": measurements_dict,
            "save_profile": req.save_profile,
            "image_base64": req.image_base64
        }
        
        order = srv.create_order(
            customer_id=req.customer_id,
            items=[item_data],
            order_date=date.today(),
            delivery_date=None,
            special_instructions=req.special_instructions,
            advance_amount=req.advance_amount
        )
        
        # Trigger desktop reload
        if bridge_instance:
            bridge_instance.notification_requested.emit("Success", f"New Order Created: {order.order_number}")
            if hasattr(bridge_instance, "order_added"):
                bridge_instance.order_added.emit()
                
        return {"status": "success", "order_id": order.id, "order_number": order.order_number}
    except Exception as e:
        logger.error(f"Failed to create mobile order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def index():
    # Return the mobile portal HTML
    index_path = os.path.join(mobile_assets_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Worker Portal not found</h1>"

class WebServerThread(Thread):
    def __init__(self, host="0.0.0.0", port=8000):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.server = None

    def run(self):
        logger.info(f"Starting Worker Portal server on {self.host}:{self.port}")
        config = uvicorn.Config(app, host=self.host, port=self.port, log_level="info", access_log=False)
        self.server = uvicorn.Server(config)
        self.server.run()
        
    def stop(self):
        if self.server:
            self.server.should_exit = True
