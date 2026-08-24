from PySide6.QtCore import QObject, Slot, Signal, Property
import json
from datetime import date, datetime
from app.services.report_service import ReportService
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.whatsapp_service import WhatsAppService
import threading
import os
import shutil
import glob
from app.config import APP_DATA_DIR
from app.printing.receipt_printer import generate_receipt_pdf
from app.web import tunnel

class WebBridge(QObject):
    """Bridge between Javascript and Python."""
    
    navigate_requested = Signal(str)
    backup_requested = Signal()
    restore_requested = Signal()
    notification_requested = Signal(str, str)
    dictation_result_requested = Signal(str, str, str)
    
    def __init__(self, services, parent=None):
        super().__init__(parent)
        self.services = services
        from app.services.dictation_service import DictationService
        self.dictation_service = DictationService(self)
        self.dictation_service.dictation_finished.connect(self.dictation_result_requested.emit)

    @Slot(str)
    def log(self, message):
        print(f"[JS] {message}")

    def _get_shop_name(self) -> str:
        try:
            from app.database.engine import get_session
            from app.repositories.settings_repo import SettingsRepository
            session = get_session()
            try:
                settings = SettingsRepository(session).get_settings()
                return settings.shop_name or "Tailor Shop"
            finally:
                session.close()
        except Exception:
            return "Tailor Shop"

    def _trigger_whatsapp_receipt(self, order_id: int):
        def _run():
            try:
                receipts_dir = os.path.join(APP_DATA_DIR, "receipts")
                os.makedirs(receipts_dir, exist_ok=True)
                pdf_path = os.path.join(receipts_dir, f"receipt_{order_id}.pdf")
                if generate_receipt_pdf(order_id, pdf_path):
                    whatsapp = WhatsAppService()
                    order = OrderService().get_order(order_id)
                    shop_name = self._get_shop_name()
                    if order and order.customer and order.customer.mobile:
                        paid_amt = order.total_amount - order.remaining_amount
                        msg = (
                            f"✨ नमस्ते {order.customer.name}! ✨\n\n"
                            f"{shop_name} को चुनने के लिए धन्यवाद! आपका ऑर्डर #{order.order_number} सफलतापूर्वक दर्ज कर लिया गया है।\n\n"
                            f"👔 कुल बिल: ₹{order.total_amount}\n"
                            f"✅ जमा किए: ₹{paid_amt}\n"
                            f"⏳ बकाया राशि: ₹{order.remaining_amount}\n\n"
                            f"हमने आपका आधिकारिक रसीद (Receipt) पीडीएफ नीचे संलग्न कर दिया है।\n"
                            f"जैसे ही आपके कपड़े तैयार हो जाएंगे, हम आपको सूचित कर देंगे!\n\n"
                            f"धन्यवाद,\n{shop_name}"
                        )
                        auth_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".wwebjs_auth"))
                        if not os.path.exists(auth_path):
                            self.notification_requested.emit("Please connect with WhatsApp Web in Settings", "error")
                        else:
                            self.notification_requested.emit("Sending WhatsApp message...", "info")
                            success = whatsapp.send_whatsapp_message(order.customer.mobile, msg, pdf_path=pdf_path)
                            if success:
                                self.notification_requested.emit("WhatsApp message sent successfully!", "success")
                            else:
                                self.notification_requested.emit("Failed to send WhatsApp message", "error")
            except Exception as e:
                print(f"WhatsApp receipt trigger error: {e}")
        threading.Thread(target=_run, daemon=True).start()

    def _trigger_whatsapp_status(self, order_id: int, status: str):
        if status != "COMPLETED" and status != "READY":
            return
        def _run():
            try:
                whatsapp = WhatsAppService()
                order = OrderService().get_order(order_id)
                shop_name = self._get_shop_name()
                if order and order.customer and order.customer.mobile:
                    items_str = ", ".join(f"{item.quantity} {item.clothing_type}" for item in order.items) if order.items else "कपड़े"
                    msg = (
                        f"🎉 खुशखबरी, {order.customer.name}! 🎉\n\n"
                        f"आपका ऑर्डर #{order.order_number} ({items_str}) अब बिल्कुल तैयार है! आप इसे {shop_name} से ले जा सकते हैं।\n\n"
                        f"कृपया अपनी सुविधा अनुसार दुकान पर आएं और अपने सिले हुए कपड़े प्राप्त करें।\n\n"
                        f"जल्द मिलेंगे!\n{shop_name}"
                    )
                    auth_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".wwebjs_auth"))
                    if not os.path.exists(auth_path):
                        self.notification_requested.emit("Please connect with WhatsApp Web in Settings", "error")
                    else:
                        self.notification_requested.emit("Sending WhatsApp message...", "info")
                        success = whatsapp.send_whatsapp_message(order.customer.mobile, msg)
                        if success:
                            self.notification_requested.emit("WhatsApp message sent successfully!", "success")
                        else:
                            self.notification_requested.emit("Failed to send WhatsApp message", "error")
            except Exception as e:
                print(f"WhatsApp status trigger error: {e}")
        threading.Thread(target=_run, daemon=True).start()

    @Slot(str, str, result=str)
    def dispatch(self, action, payload_str):
        print(f"[Bridge] Dispatch Action: {action}")
        try:
            from app.database.engine import get_session
            session = get_session()
            # Force close any pending transaction on this thread's session to ensure fresh reads
            session.commit()
            
            payload = json.loads(payload_str) if payload_str else {}
        except json.JSONDecodeError:
            payload = {}

        response = {"status": "error", "message": "Unknown action"}
        
        try:
            # ────────────────────────────────────────────────────────────
            # NAVIGATION
            # ────────────────────────────────────────────────────────────
            if action == "navigate_to":
                page = payload.get("page", "dashboard")
                self.navigate_requested.emit(page)
                response = {"status": "success"}

            # ────────────────────────────────────────────────────────────
            # DICTATION
            # ────────────────────────────────────────────────────────────
            elif action == "start_dictation":
                textarea_id = payload.get("textarea_id")
                self.dictation_service.start_recording(textarea_id)
                response = {"status": "success"}
                
            elif action == "stop_dictation":
                language = payload.get("language", "hi-IN")
                self.dictation_service.stop_recording(language)
                response = {"status": "success"}

            # ────────────────────────────────────────────────────────────
            # WORKER PORTAL
            # ────────────────────────────────────────────────────────────
            elif action == "get_worker_portal_url":
                tunnel_url = getattr(self.parent(), "tunnel_url", None)
                if tunnel_url:
                    response = {"status": "success", "data": {"url": tunnel_url}}
                else:
                    response = {"status": "error", "message": "Portal is not running"}

            elif action == "get_all_workers":
                worker_srv = self.services["worker"]
                workers = worker_srv.get_all_workers()
                response = {"status": "success", "data": {"workers": workers}}

            elif action == "add_worker":
                worker_srv = self.services["worker"]
                w = worker_srv.add_worker(
                    payload.get("name"), 
                    payload.get("phone"), 
                    payload.get("pin"),
                    payload.get("worker_type", "PIECE_RATE"),
                    float(payload.get("daily_rate", 0.0))
                )
                response = {"status": "success", "data": {"worker": w}}

            elif action == "assign_task":
                worker_srv = self.services["worker"]
                t = worker_srv.assign_task(payload.get("worker_id"), payload.get("order_item_id"), payload.get("payout_amount"))
                response = {"status": "success", "data": {"task": t}}
                
            elif action == "get_worker_tasks":
                worker_srv = self.services["worker"]
                t = worker_srv.get_worker_tasks(payload.get("worker_id"))
                response = {"status": "success", "data": {"tasks": t}}

            elif action == "get_garment_rates":
                worker_srv = self.services["worker"]
                rates = worker_srv.get_garment_rates()
                response = {"status": "success", "data": {"rates": rates}}

            elif action == "set_garment_rate":
                worker_srv = self.services["worker"]
                rate = worker_srv.set_garment_rate(payload.get("garment_type"), float(payload.get("rate", 0)))
                response = {"status": "success", "data": {"rate": rate}}

            elif action == "get_all_pending_entries":
                worker_srv = self.services["worker"]
                entries = worker_srv.get_all_pending_entries()
                response = {"status": "success", "data": {"entries": entries}}

            elif action == "approve_entry":
                worker_srv = self.services["worker"]
                success = worker_srv.approve_entry(payload.get("entry_id"), payload.get("status"))
                response = {"status": "success" if success else "error"}

            elif action == "record_advance":
                worker_srv = self.services["worker"]
                advance = worker_srv.record_advance(payload.get("worker_id"), float(payload.get("amount", 0)), payload.get("notes", ""))
                response = {"status": "success", "data": {"advance": advance}}

            elif action == "get_worker_ledger":
                worker_srv = self.services["worker"]
                ledger = worker_srv.get_worker_ledger(payload.get("worker_id"))
                response = {"status": "success", "data": {"ledger": ledger}}


            # ────────────────────────────────────────────────────────────
            # DASHBOARD
            # ────────────────────────────────────────────────────────────
            elif action == "get_dashboard_stats":
                from datetime import date
                order_srv = self.services["order"]
                target_date = None
                date_str = payload.get("date")
                if date_str:
                    try:
                        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except ValueError:
                        pass
                dash_data = order_srv.get_dashboard_data(target_date)
                
                recent_orders = []
                for o in dash_data["recent_orders"]:
                    recent_orders.append({
                        "id": o.id,
                        "order_number": o.order_number,
                        "customer_name": o.customer.name if o.customer else "Unknown",
                        "status": o.status
                    })
                    
                deliveries = []
                for o in dash_data["today_deliveries_list"]:
                    deliveries.append({
                        "id": o.id,
                        "order_number": o.order_number,
                        "customer_name": o.customer.name if o.customer else "Unknown",
                        "status": o.status,
                        "remaining": o.remaining_amount,
                        "items": "Various"
                    })

                data = {
                    "orders_today": dash_data["orders_today"],
                    "sales_today": dash_data["today_sales"],
                    "pending_payments": dash_data["pending_payments"],
                    "deliveries_today": dash_data["deliveries_today"],
                    "status_counts": dash_data["status_counts"],
                    "recent_orders": recent_orders,
                    "deliveries": deliveries
                }
                response = {"status": "success", "data": data}

            # ────────────────────────────────────────────────────────────
            # CUSTOMERS
            # ────────────────────────────────────────────────────────────
            elif action == "get_customers":
                from app.database.engine import get_session
                session = get_session()
                try:
                    from app.models.customer import Customer
                    from app.models.order import Order
                    
                    # Clear session just to be safe if any detached objects linger
                    session.expunge_all()
                    
                    customers = session.query(Customer).filter(Customer.is_active == True).order_by(Customer.id.desc()).all()  # noqa: E712
                    data = []
                    for c in customers:
                        orders = session.query(Order).filter(Order.customer_id == c.id).all()
                        count = len(orders)
                        pending_amount = sum(o.remaining_amount for o in orders)
                        last_order_date = max([o.order_date for o in orders if o.order_date], default=None)
                        data.append({
                            "id": c.id,
                            "name": c.name,
                            "mobile": c.mobile,
                            "address": c.address or "",
                            "notes": c.notes or "",
                            "orders_count": count,
                            "pending_amount": pending_amount,
                            "last_order": last_order_date.isoformat() if last_order_date else "-",
                            "is_active": c.is_active
                        })
                    response = {"status": "success", "data": data}
                finally:
                    session.close()
            
            elif action == "get_customer_details":
                from app.database.engine import get_session
                session = get_session()
                try:
                    from app.models.customer import Customer
                    from app.models.order import Order
                    from app.models.measurement import MeasurementProfile
                    
                    cust_id = payload.get("id")
                    c = session.query(Customer).filter(Customer.id == cust_id).first()
                    if not c:
                        raise Exception("Customer not found")
                        
                    orders = session.query(Order).filter(Order.customer_id == c.id).all()
                    
                    order_data = []
                    for o in orders:
                        order_data.append({
                            "id": o.id,
                            "order_number": o.order_number,
                            "clothing_type": o.items[0].clothing_type if o.items else "Custom",
                            "order_date": o.order_date.isoformat() if o.order_date else "",
                            "delivery_date": o.delivery_date.isoformat() if o.delivery_date else "",
                            "status": o.status,
                            "total_amount": o.total_amount,
                            "remaining_amount": o.remaining_amount
                        })
                        
                    profiles = session.query(MeasurementProfile).filter(MeasurementProfile.customer_id == c.id).all()
                    profile_data = []
                    for p in profiles:
                        vals = {}
                        for v in p.values:
                            vals[v.field_name] = v.field_value
                        profile_data.append({
                            "id": p.id,
                            "template_type": p.template_type,
                            "updated_at": p.updated_at.isoformat() if p.updated_at else "",
                            "values": vals
                        })
                        
                    data = {
                        "customer": {
                            "id": c.id,
                            "name": c.name,
                            "mobile": c.mobile,
                            "address": c.address or "",
                            "notes": c.notes or ""
                        },
                        "orders": order_data,
                        "profiles": profile_data
                    }
                    response = {"status": "success", "data": data}
                finally:
                    session.close()

            elif action == "create_customer":
                cust_srv: CustomerService = self.services['customer']
                customer = cust_srv.create_customer(
                    name=payload.get('name'),
                    mobile=payload.get('mobile'),
                    address=payload.get('address'),
                    notes=payload.get('notes')
                )
                response = {"status": "success", "data": {"id": customer.id}}

            elif action == "update_customer":
                cust_srv: CustomerService = self.services['customer']
                cust_id = payload.get("id")
                cust_srv.update_customer(
                    cust_id,
                    name=payload.get('name'),
                    mobile=payload.get('mobile'),
                    address=payload.get('address'),
                    notes=payload.get('notes')
                )
                response = {"status": "success"}

            elif action == "delete_customer":
                from app.database.engine import get_session
                from app.models.customer import Customer
                customer_id = int(payload.get("id"))
                del_session = get_session()
                try:
                    c = del_session.query(Customer).filter(Customer.id == customer_id).first()
                    if c:
                        del_session.delete(c)
                        del_session.commit()
                        print(f"[Delete] Customer {customer_id} physically deleted along with all related records.")
                        response = {"status": "success"}
                    else:
                        response = {"status": "error", "message": f"Customer not found (ID: {customer_id})"}
                except Exception as e:
                    del_session.rollback()
                    print(f"[Delete] Error: {e}")
                    response = {"status": "error", "message": str(e)}
                finally:
                    del_session.close()


            # ────────────────────────────────────────────────────────────
            # MEASUREMENTS
            # ────────────────────────────────────────────────────────────
            elif action == "get_all_measurements":
                from app.database.engine import get_session
                session = get_session()
                try:
                    from app.models.measurement import MeasurementProfile
                    from app.models.customer import Customer
                    
                    # Clear session just to be safe
                    session.expunge_all()
                    
                    measurements = session.query(MeasurementProfile).all()
                    data = []
                    for m in measurements:
                        customer = session.query(Customer).filter(Customer.id == m.customer_id).first()
                        
                        data.append({
                            "id": m.id,
                            "name": m.name,
                            "customer_name": customer.name if customer else "Unknown",
                            "customer_mobile": customer.mobile if customer else "",
                            "template_type": m.template_type,
                            "values_count": len(m.values), # Values are cascade-loaded or we can just let lazy load happen safely since session is open and clean
                            "updated_at": m.updated_at.isoformat()
                        })
                    response = {"status": "success", "data": data}
                finally:
                    session.close()

            # ────────────────────────────────────────────────────────────
            # ────────────────────────────────────────────────────────────
            # MEASUREMENTS FOR CUSTOMER (WIZARD)
            # ────────────────────────────────────────────────────────────
            elif action == "get_measurements_for_customer":
                cust_id = payload.get("customer_id")
                meas_srv = self.services["measurement"]
                measurements = meas_srv.get_profiles_for_customer(cust_id)
                data = []
                for m in measurements:
                    vals = {}
                    for v in m.values:
                        vals[v.field_name] = v.field_value
                    data.append({
                        "id": m.id,
                        "template_type": m.template_type,
                        "values": vals,
                        "updated_at": m.updated_at.isoformat()
                    })
                response = {"status": "success", "data": data}
                
            elif action == "create_measurement":
                cust_id = payload.get("customer_id")
                template = payload.get("template_type", "Shirt")
                name = payload.get("name", f"{template} Profile")
                values = payload.get("values", {})
                notes = payload.get("notes", "")
                
                if not cust_id:
                    raise ValueError("customer_id is required")
                    
                meas_srv = self.services["measurement"]
                m = meas_srv.create_profile(
                    customer_id=cust_id,
                    template_type=template,
                    name=name,
                    values=values,
                    notes=notes
                )
                response = {"status": "success", "data": {"id": m.id}}

            # ────────────────────────────────────────────────────────────
            # ORDERS
            # ────────────────────────────────────────────────────────────
            elif action == "create_order":
                order_srv = self.services["order"]
                
                # Parse date string to date object
                deliv_str = payload.get("deliveryDate")
                deliv_date = None
                if deliv_str:
                    deliv_date = datetime.strptime(deliv_str, "%Y-%m-%d").date()
                
                items = payload.get("items", [])
                if not items:
                    # Backward compatibility fallback
                    items = [{
                        "clothing_type": payload.get("clothingType", "Custom"),
                        "quantity": payload.get("quantity", 1),
                        "price": float(payload.get("price", 0)),
                        "measurement_profile_id": payload.get("measurementId")
                    }]

                send_whatsapp = payload.get("send_whatsapp", True)
                
                order = order_srv.create_order(
                    customer_id=payload.get("customerId"),
                    items=items,
                    order_date=datetime.now().date(),
                    delivery_date=deliv_date,
                    special_instructions=payload.get("notes", ""),
                    advance_amount=float(payload.get("advance", 0)),
                    payment_method=payload.get("paymentMethod", "Cash")
                )
                
                # Wait for WhatsApp message to send if checked
                if send_whatsapp:
                    auth_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".wwebjs_auth"))
                    if not os.path.exists(auth_path):
                        order_srv.delete_order(order.id)
                        raise Exception("Please connect with WhatsApp Web in Settings first.")
                    
                    try:
                        receipts_dir = os.path.join(APP_DATA_DIR, "receipts")
                        os.makedirs(receipts_dir, exist_ok=True)
                        pdf_path = os.path.join(receipts_dir, f"receipt_{order.id}.pdf")
                        
                        if generate_receipt_pdf(order.id, pdf_path):
                            whatsapp = WhatsAppService()
                            shop_name = self._get_shop_name()
                            customer_srv = self.services["customer"]
                            customer = customer_srv.get_customer(payload.get("customerId")) if payload.get("customerId") else None
                            
                            if customer and customer.mobile:
                                paid_amt = order.total_amount - order.remaining_amount
                                msg = (
                                    f"✨ नमस्ते {customer.name}! ✨\n\n"
                                    f"{shop_name} को चुनने के लिए धन्यवाद! आपका ऑर्डर #{order.order_number} सफलतापूर्वक दर्ज कर लिया गया है।\n\n"
                                    f"👔 कुल बिल: ₹{order.total_amount}\n"
                                    f"✅ जमा किए: ₹{paid_amt}\n"
                                    f"⏳ बकाया राशि: ₹{order.remaining_amount}\n\n"
                                    f"हमने आपका आधिकारिक रसीद (Receipt) पीडीएफ नीचे संलग्न कर दिया है।\n"
                                    f"जैसे ही आपके कपड़े तैयार हो जाएंगे, हम आपको सूचित कर देंगे!\n\n"
                                    f"धन्यवाद,\n{shop_name}"
                                )
                                self.notification_requested.emit("Sending WhatsApp message...", "info")
                                success = whatsapp.send_whatsapp_message(customer.mobile, msg, pdf_path=pdf_path)
                                if not success:
                                    order_srv.delete_order(order.id)
                                    raise Exception("Failed to send WhatsApp message. Order was not saved.")
                                self.notification_requested.emit("WhatsApp message sent successfully!", "success")
                    except Exception as e:
                        # Fallback deletion if something crashed
                        try:
                            order_srv.delete_order(order.id)
                        except:
                            pass
                        raise Exception(str(e))

                response = {
                    "status": "success", 
                    "data": {"id": order.id, "order_number": order.order_number}
                }
                
            elif action == "update_order":
                order_srv = self.services["order"]
                order_id = payload.get("orderId")
                
                deliv_str = payload.get("deliveryDate")
                deliv_date = None
                if deliv_str:
                    deliv_date = datetime.strptime(deliv_str, "%Y-%m-%d").date()
                
                items = payload.get("items", [])
                
                order = order_srv.update_order(
                    order_id=order_id,
                    items=items,
                    delivery_date=deliv_date,
                    special_instructions=payload.get("notes", "")
                )
                
                response = {
                    "status": "success", 
                    "data": {"id": order.id, "order_number": order.order_number}
                }
                
            elif action == "get_all_orders":
                order_srv = self.services["order"]
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
                        "order_date": o.order_date.isoformat() if o.order_date else "",
                        "delivery_date": o.delivery_date.isoformat() if o.delivery_date else "",
                        "status": o.status,
                        "total_amount": o.total_amount,
                        "remaining_amount": o.remaining_amount
                    })
                response = {"status": "success", "data": data}
                
            elif action == "get_order_details":
                from app.database.engine import get_session
                session = get_session()
                try:
                    from app.models.order import Order
                    order_id = payload.get("id")
                    o = session.query(Order).filter(Order.id == order_id).first()
                    if not o:
                        raise Exception("Order not found")
                        
                    c = o.customer
                    
                    payments = []
                    for p in o.payments:
                        payments.append({
                            "id": p.id,
                            "amount": p.amount,
                            "payment_date": p.payment_date.isoformat() if p.payment_date else "",
                            "payment_method": p.payment_method
                        })
                        
                    tunnel_url = tunnel.GLOBAL_TUNNEL_URL or "http://localhost:8000"
                    scan_url = f"{tunnel_url}/scan?order_id={o.id}"

                    data = {
                        "id": o.id,
                        "order_number": o.order_number,
                        "customer_id": c.id if c else None,
                        "customer_name": c.name if c else "Unknown",
                        "customer_mobile": c.mobile if c else "",
                        "customer_address": c.address if c else "",
                        "order_date": o.order_date.isoformat() if o.order_date else "",
                        "delivery_date": o.delivery_date.isoformat() if o.delivery_date else "",
                        "status": o.status,
                        "total_amount": o.total_amount,
                        "advance_amount": o.advance_amount,
                        "remaining_amount": o.remaining_amount,
                        "special_instructions": o.special_instructions or "",
                        "scan_url": scan_url,
                        "payments": payments,
                        "items": []
                    }
                    
                    for item in o.items:
                        item_data = {
                            "id": item.id,
                            "clothing_type": item.clothing_type,
                            "quantity": item.quantity,
                            "price": item.price,
                            "notes": item.notes or "",
                            "image_path": getattr(item, "image_path", None) or "",
                            "measurements": {}
                        }
                        for m in item.measurements:
                            item_data["measurements"][m.field_name] = m.field_value
                        data["items"].append(item_data)
                        
                    response = {"status": "success", "data": data}
                finally:
                    session.close()
                
            elif action == "update_order_status":
                order_srv = self.services["order"]
                status = payload.get("status")
                order_id = payload.get("order_id") or payload.get("id")
                send_whatsapp = payload.get("send_whatsapp", False)
                
                if send_whatsapp and (status == "COMPLETED" or status == "READY" or status == "DELIVERED"):
                    auth_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".wwebjs_auth"))
                    if not os.path.exists(auth_path):
                        raise Exception("Please connect with WhatsApp Web in Settings first.")
                    
                    whatsapp = WhatsAppService()
                    order = order_srv.get_order(order_id)
                    shop_name = self._get_shop_name()
                    if order and order.customer and order.customer.mobile:
                        items_str = ", ".join(f"{item.quantity} {item.clothing_type}" for item in order.items) if order.items else "कपड़े"
                        msg = (
                            f"🎉 खुशखबरी, {order.customer.name}! 🎉\n\n"
                            f"आपका ऑर्डर #{order.order_number} ({items_str}) अब बिल्कुल तैयार है! आप इसे {shop_name} से ले जा सकते हैं।\n\n"
                            f"कृपया अपनी सुविधा अनुसार दुकान पर आएं और अपने सिले हुए कपड़े प्राप्त करें।\n\n"
                            f"जल्द मिलेंगे!\n{shop_name}"
                        )
                        self.notification_requested.emit("Sending WhatsApp message...", "info")
                        success = whatsapp.send_whatsapp_message(order.customer.mobile, msg)
                        if not success:
                            raise Exception("Failed to send WhatsApp message. Status was not updated.")
                        self.notification_requested.emit("WhatsApp message sent successfully!", "success")
                
                order_srv.update_status(order_id, status)
                response = {"status": "success"}

            elif action == "connect_whatsapp":
                def _run():
                    whatsapp = WhatsAppService()
                    whatsapp.connect_whatsapp()
                threading.Thread(target=_run, daemon=True).start()
                response = {"status": "success"}

            # ────────────────────────────────────────────────────────────
            # PAYMENTS
            # ────────────────────────────────────────────────────────────
            elif action == "get_all_payments":
                from app.database.engine import get_session
                from app.repositories.payment_repo import PaymentRepository
                session = get_session()
                try:
                    repo = PaymentRepository(session)
                    payments = repo.get_all()
                    data = []
                    for p in payments:
                        data.append({
                            "id": p.id,
                            "order_id": p.order_id,
                            "order_number": p.order.order_number if p.order else "",
                            "customer_name": p.customer.name if p.customer else "",
                            "customer_mobile": p.customer.mobile if p.customer else "",
                            "amount": p.amount,
                            "payment_date": p.payment_date.isoformat() if p.payment_date else "",
                            "payment_method": p.payment_method
                        })
                    response = {"status": "success", "data": data}
                finally:
                    session.close()

            elif action == "get_payments_dashboard":
                from app.database.engine import get_session
                from app.models.payment import Payment
                from app.models.order import Order
                from datetime import date
                session = get_session()
                try:
                    today = date.today()
                    
                    # Total collected
                    all_payments = session.query(Payment).all()
                    total_collected = sum(p.amount for p in all_payments)
                    
                    # Today's payments
                    today_payments = sum(p.amount for p in all_payments if p.payment_date == today)
                    
                    # Pending payments (remaining amount on all active orders)
                    active_orders = session.query(Order).filter(Order.status != 'CANCELLED').all()
                    pending_payments = sum(o.remaining_amount for o in active_orders if o.remaining_amount > 0)
                    
                    data = {
                        "total_collected": total_collected,
                        "pending_payments": pending_payments,
                        "today_payments": today_payments
                    }
                    response = {"status": "success", "data": data}
                finally:
                    session.close()
                    
            elif action == "create_payment":
                pay_srv = self.services["payment"]
                from datetime import date
                order_id = payload.get("order_id")
                send_whatsapp = payload.get("send_whatsapp", True)
                
                payment = pay_srv.add_payment(
                    order_id=order_id,
                    amount=float(payload.get("amount")),
                    payment_method=payload.get("payment_method", "Cash"),
                    payment_date=date.today()
                )
                
                if send_whatsapp:
                    auth_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".wwebjs_auth"))
                    if not os.path.exists(auth_path):
                        pay_srv.delete_payment(payment.id)
                        raise Exception("Please connect with WhatsApp Web in Settings first.")
                    
                    try:
                        receipts_dir = os.path.join(APP_DATA_DIR, "receipts")
                        os.makedirs(receipts_dir, exist_ok=True)
                        pdf_path = os.path.join(receipts_dir, f"receipt_{order_id}.pdf")
                        
                        if generate_receipt_pdf(order_id, pdf_path):
                            whatsapp = WhatsAppService()
                            order_srv = self.services["order"]
                            order = order_srv.get_order(order_id)
                            shop_name = self._get_shop_name()
                            if order and order.customer and order.customer.mobile:
                                paid_amt = order.total_amount - order.remaining_amount
                                msg = (
                                    f"✨ नमस्ते {order.customer.name}! ✨\n\n"
                                    f"हमने आपके ऑर्डर #{order.order_number} के लिए ₹{payment.amount} का भुगतान प्राप्त कर लिया है।\n\n"
                                    f"✅ कुल जमा: ₹{paid_amt}\n"
                                    f"⏳ बकाया राशि: ₹{order.remaining_amount}\n\n"
                                    f"हमने आपकी अपडेटेड रसीद (Receipt) संलग्न कर दी है।\n\n"
                                    f"धन्यवाद,\n{shop_name}"
                                )
                                self.notification_requested.emit("Sending WhatsApp payment receipt...", "info")
                                success = whatsapp.send_whatsapp_message(order.customer.mobile, msg, pdf_path=pdf_path)
                                if not success:
                                    pay_srv.delete_payment(payment.id)
                                    raise Exception("Failed to send WhatsApp message. Payment was not recorded.")
                                self.notification_requested.emit("WhatsApp message sent successfully!", "success")
                    except Exception as e:
                        try:
                            pay_srv.delete_payment(payment.id)
                        except:
                            pass
                        raise Exception(str(e))
                
                response = {"status": "success"}

            # ────────────────────────────────────────────────────────────
            # DELIVERIES
            # ────────────────────────────────────────────────────────────
            elif action == "get_deliveries_dashboard":
                from datetime import date, timedelta
                order_srv = self.services["order"]
                today = date.today()
                tomorrow = today + timedelta(days=1)
                
                orders = order_srv.get_all_orders()
                deliveries = []
                counts = {"due_today": 0, "due_tomorrow": 0, "upcoming": 0, "overdue": 0}
                
                for o in orders:
                    # The user requested that the Deliveries dashboard ONLY show 'READY' products.
                    if o.status != "READY": continue
                    
                    if o.delivery_date:
                        if o.delivery_date < today:
                            counts["overdue"] += 1
                        elif o.delivery_date == today:
                            counts["due_today"] += 1
                        elif o.delivery_date == tomorrow:
                            counts["due_tomorrow"] += 1
                        else:
                            counts["upcoming"] += 1
                            
                    deliveries.append({
                        "id": o.id,
                        "order_number": o.order_number,
                        "customer_name": o.customer.name if o.customer else "",
                        "mobile": o.customer.mobile if o.customer else "",
                        "items": "Various",
                        "delivery_date": o.delivery_date.isoformat() if o.delivery_date else "",
                        "status": o.status,
                        "total_amount": o.total_amount,
                        "advance_paid": getattr(o, "advance_amount", getattr(o, "paid_amount", 0))
                    })
                
                deliveries.sort(key=lambda x: x["delivery_date"])
                response = {"status": "success", "data": {"counts": counts, "deliveries": deliveries}}

            # ────────────────────────────────────────────────────────────
            # EXPENSES
            # ────────────────────────────────────────────────────────────
            elif action == "get_expenses_dashboard":
                exp_srv = self.services["expense"]
                expenses = exp_srv.get_all_expenses()
                data = []
                for e in expenses:
                    data.append({
                        "id": e.id,
                        "date": e.date.isoformat() if e.date else "",
                        "category": e.category,
                        "amount": e.amount,
                        "description": e.description or "",
                        "payment_method": e.payment_method
                    })
                from datetime import date, timedelta
                today = date.today()
                week_start = today - timedelta(days=today.weekday())
                month_start = today.replace(day=1)
                
                stats = {"today": 0, "week": 0, "month": 0}
                for e in expenses:
                    if e.date:
                        if e.date == today:
                            stats["today"] += e.amount
                        if e.date >= week_start:
                            stats["week"] += e.amount
                        if e.date >= month_start:
                            stats["month"] += e.amount
                response = {"status": "success", "data": {"expenses": data, "stats": stats}}
                
            elif action == "create_expense":
                exp_srv = self.services["expense"]
                from datetime import date
                exp_srv.create_expense(
                    category=payload.get("category"),
                    amount=payload.get("amount"),
                    description=payload.get("description"),
                    payment_method=payload.get("payment_method"),
                    date=date.today()
                )
                response = {"status": "success"}

            # ────────────────────────────────────────────────────────────
            # REPORTS
            # ────────────────────────────────────────────────────────────
            elif action == "get_report_data":
                rep_srv = self.services["report"]
                data = rep_srv.get_this_month_report()
                response = {"status": "success", "data": {
                    "total_sales": data.get("total_sales", 0),
                    "total_orders": data.get("total_orders", 0),
                    "total_expenses": data.get("total_expenses", 0),
                    "net_profit": data.get("estimated_profit", 0)
                }}

            # ────────────────────────────────────────────────────────────
            # SETTINGS
            # ────────────────────────────────────────────────────────────
            elif action == "get_settings":
                from app.database.engine import get_session
                from app.repositories.settings_repo import SettingsRepository
                session = get_session()
                try:
                    repo = SettingsRepository(session)
                    s = repo.get_settings()
                    response = {"status": "success", "data": {
                        "shop_name": s.shop_name,
                        "owner_name": s.owner_name,
                        "phone": s.phone,
                        "address": s.address,
                        "currency_symbol": s.currency,
                        "measurement_unit": s.measurement_unit,
                        "twilio_account_sid": s.twilio_account_sid,
                        "twilio_auth_token": s.twilio_auth_token,
                        "twilio_sender_number": s.twilio_sender_number
                    }}
                finally:
                    session.close()
                    
            elif action == "update_settings":
                from app.database.engine import get_session
                from app.repositories.settings_repo import SettingsRepository
                session = get_session()
                try:
                    repo = SettingsRepository(session)
                    repo.update_settings(**payload)
                    session.commit()
                    response = {"status": "success"}
                finally:
                    session.close()

            elif action == "create_backup":
                db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'tailor_shop.db'))
                backup_dir = os.path.expanduser('~/Documents/ArtisanStitch_Backups')
                os.makedirs(backup_dir, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
                
                if os.path.exists(db_path):
                    shutil.copy2(db_path, backup_path)
                    response = {"status": "success", "path": backup_path}
                else:
                    response = {"status": "error", "message": "Database file not found"}

            elif action == "restore_backup":
                # In a real app we'd let the user select the file, but for now we restore the latest backup.
                db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'tailor_shop.db'))
                backup_dir = os.path.expanduser('~/Documents/ArtisanStitch_Backups')
                backups = glob.glob(os.path.join(backup_dir, '*.db'))
                
                if backups:
                    latest_backup = max(backups, key=os.path.getctime)
                    shutil.copy2(latest_backup, db_path)
                    response = {"status": "success"}
                else:
                    response = {"status": "error", "message": "No backups found to restore."}

            else:
                response = {"status": "error", "message": f"Unknown action: {action}"}
        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": "error", "message": str(e)}

        return json.dumps(response)
