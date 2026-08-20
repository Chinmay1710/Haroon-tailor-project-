with open("app/ui/web_bridge.py", "a", encoding="utf-8") as f:
    f.write('''
            # ────────────────────────────────────────────────────────────
            # MEASUREMENTS FOR CUSTOMER (WIZARD)
            # ────────────────────────────────────────────────────────────
            elif action == "get_measurements_for_customer":
                cust_id = payload.get("customer_id")
                meas_srv = self.services["measurement"]
                measurements = meas_srv.get_customer_measurements(cust_id)
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

            # ────────────────────────────────────────────────────────────
            # ORDERS
            # ────────────────────────────────────────────────────────────
            elif action == "get_all_orders":
                order_srv = self.services["order"]
                orders = order_srv.get_all_orders()
                data = []
                for o in orders:
                    data.append({
                        "id": o.id,
                        "order_number": o.order_number,
                        "customer_name": o.customer.name if o.customer else "Unknown",
                        "items": "Various",
                        "order_date": o.order_date.isoformat() if o.order_date else "",
                        "delivery_date": o.delivery_date.isoformat() if o.delivery_date else "",
                        "status": o.status,
                        "total_amount": o.total_amount
                    })
                response = {"status": "success", "data": data}
                
            elif action == "update_order_status":
                order_srv = self.services["order"]
                order_srv.update_order_status(payload.get("order_id"), payload.get("status"))
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
                            "amount": p.amount,
                            "payment_date": p.payment_date.isoformat() if p.payment_date else "",
                            "payment_method": p.payment_method
                        })
                    response = {"status": "success", "data": data}
                finally:
                    session.close()

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
                    if o.status in ["DELIVERED", "CANCELLED"]: continue
                    
                    if o.delivery_date:
                        if o.delivery_date.date() < today:
                            counts["overdue"] += 1
                        elif o.delivery_date.date() == today:
                            counts["due_today"] += 1
                        elif o.delivery_date.date() == tomorrow:
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
                        "status": o.status
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
                # Fake stats for now, real calculation is easy
                stats = {"today": 0, "week": 0, "month": 0}
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
                data = rep_srv.get_dashboard_summary()
                response = {"status": "success", "data": {
                    "total_sales": data.get("total_sales", 0),
                    "total_orders": data.get("total_orders", 0),
                    "total_expenses": data.get("total_expenses", 0),
                    "net_profit": data.get("total_sales", 0) - data.get("total_expenses", 0)
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
                        "currency_symbol": s.currency_symbol,
                        "measurement_unit": s.measurement_unit
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

            else:
                response = {"status": "error", "message": f"Unknown action: {action}"}
        except Exception as e:
            import traceback
            traceback.print_exc()
            response = {"status": "error", "message": str(e)}

        return json.dumps(response)
''')
