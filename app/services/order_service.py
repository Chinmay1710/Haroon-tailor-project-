from __future__ import annotations
"""Order service — order creation with measurement snapshot, status transitions."""

import os
import base64
import uuid
from datetime import date
from sqlalchemy.orm import joinedload
from app.database.engine import get_session
from app.repositories.order_repo import OrderRepository
from app.repositories.measurement_repo import MeasurementRepository
from app.repositories.payment_repo import PaymentRepository
from app.models.order import Order
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Valid status transitions
VALID_TRANSITIONS = {
    "NEW": ["CUTTING_COMPLETE", "STITCHING_COMPLETE", "DELIVERED", "CANCELLED"],
    "CUTTING_COMPLETE": ["STITCHING_COMPLETE", "DELIVERED", "CANCELLED", "NEW"],
    "STITCHING_COMPLETE": ["DELIVERED", "CANCELLED", "NEW", "CUTTING_COMPLETE"],
    "DELIVERED": ["STITCHING_COMPLETE", "CANCELLED"],  # Allow reverting if accidental
    "CANCELLED": ["NEW"],  # Allow reopening
    "CUTTING": ["CUTTING_COMPLETE", "STITCHING_COMPLETE", "DELIVERED", "CANCELLED", "NEW"],
    "STITCHING": ["CUTTING_COMPLETE", "STITCHING_COMPLETE", "DELIVERED", "CANCELLED", "NEW"],
    "READY": ["CUTTING_COMPLETE", "STITCHING_COMPLETE", "DELIVERED", "CANCELLED", "NEW"],
}


class OrderService:

    def _save_image(self, b64_data: str) -> str:
        """Decode base64 image and save to disk, returning relative path."""
        if not b64_data:
            return None
            
        try:
            # Handle data:image/jpeg;base64, prefix if present
            if ',' in b64_data:
                b64_data = b64_data.split(',')[1]
                
            img_data = base64.b64decode(b64_data)
            filename = f"item_{uuid.uuid4().hex[:8]}.jpg"
            
            from app.config import UPLOADS_DIR
            
            upload_dir = os.path.join(UPLOADS_DIR, "items")
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f:
                f.write(img_data)
                
            # Return relative path for DB, but the UI will need absolute path resolution
            return f"../uploads/items/{filename}"
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return None

    def create_order(self, customer_id: int, items: list[dict],
                     order_date: date, delivery_date: date | None,
                     special_instructions: str, advance_amount: float,
                     payment_method: str = "Cash") -> Order:
        """

        Create a new order with measurement snapshots for multiple items.
        """
        session = get_session()
        try:
            total_amount = sum((item.get('quantity', 1) * item.get('price', 0.0)) for item in items)

            order_repo = OrderRepository(session)
            order = order_repo.create(
                customer_id=customer_id,
                order_date=order_date,
                delivery_date=delivery_date,
                total_amount=total_amount,
                advance_amount=advance_amount,
                special_instructions=special_instructions,
            )

            # Add order items
            for item_data in items:
                b64_data = item_data.get('image_base64')
                if isinstance(b64_data, list):
                    paths = [self._save_image(b) for b in b64_data if b]
                    paths = [p for p in paths if p] # filter out Nones
                    img_path = ",".join(paths) if paths else None
                else:
                    img_path = self._save_image(b64_data)
                item = order_repo.add_item(
                    order_id=order.id,
                    clothing_type=item_data.get('clothing_type', 'Custom'),
                    quantity=item_data.get('quantity', 1),
                    price=item_data.get('price', 0.0),
                    image_path=img_path,
                    notes=item_data.get('notes', ''),
                )

                # Snapshot inline measurements for this item
                measurements = item_data.get('measurements')
                if measurements and isinstance(measurements, dict):
                    # Save measurement snapshots to the order item
                    for i, (field_name, field_value) in enumerate(measurements.items()):
                        order_repo.add_measurement_snapshot(
                            order_item_id=item.id,
                            field_name=field_name,
                            field_value=str(field_value),
                            unit="inches",
                            display_order=i,
                        )
                    
                    # Optionally save as a reusable measurement profile
                    if item_data.get('save_profile'):
                        meas_repo = MeasurementRepository(session)
                        profile_name = item_data.get('profile_name') or f"{item_data.get('clothing_type', 'Custom')} Profile"
                        profile = meas_repo.create_profile(
                            customer_id=customer_id,
                            template_type=item_data.get('clothing_type', 'Custom'),
                            name=profile_name,
                            unit="inches",
                            notes="Auto-saved from Order"
                        )
                        meas_repo.update_values(profile.id, {k: str(v) for k, v in measurements.items()})

            # Record advance payment if > 0
            if advance_amount > 0:
                pay_repo = PaymentRepository(session)
                pay_repo.create(
                    order_id=order.id,
                    customer_id=customer_id,
                    amount=advance_amount,
                    payment_date=order_date,
                    payment_method=payment_method,
                    note="Advance payment",
                )

            session.commit()
            logger.info(f"Order created: {order.order_number}")
            return order

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create order: {e}")
            raise
        finally:
            session.close()

    def update_order(self, order_id: int, items: list[dict],
                     delivery_date: date | None, special_instructions: str) -> Order:
        """
        Update an existing order's basic info and rewrite its items/measurements.
        """
        session = get_session()
        try:
            total_amount = sum((item.get('quantity', 1) * item.get('price', 0.0)) for item in items)
            order_repo = OrderRepository(session)
            
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise ValueError(f"Order {order_id} not found")
            
            # Update basic details
            order.delivery_date = delivery_date
            order.special_instructions = special_instructions
            order.total_amount = total_amount
            
            # Recreate items
            order_repo.clear_items(order_id)
            # Re-add order items
            for item_data in items:
                b64_data = item_data.get('image_base64')
                if isinstance(b64_data, list):
                    paths = [self._save_image(b) for b in b64_data if b]
                    paths = [p for p in paths if p] # filter out Nones
                    img_path = ",".join(paths) if paths else None
                else:
                    img_path = self._save_image(b64_data)
                item = order_repo.add_item(
                    order_id=order.id,
                    clothing_type=item_data.get('clothing_type', 'Custom'),
                    quantity=item_data.get('quantity', 1),
                    price=item_data.get('price', 0.0),
                    image_path=img_path,
                    notes=item_data.get('notes', ''),
                )
                
                measurements = item_data.get('measurements', {})
                for idx, (field_name, field_value) in enumerate(measurements.items()):
                    if field_value:
                        order_repo.add_measurement_snapshot(
                            order_item_id=item.id,
                            field_name=field_name,
                            field_value=str(field_value),
                            display_order=idx
                        )
                
                if item_data.get('save_profile'):
                    meas_repo = MeasurementRepository(session)
                    profile_name = item_data.get('profile_name') or f"{item_data.get('clothing_type', 'Custom')} Profile"
                    profile = meas_repo.create_profile(
                        customer_id=order.customer_id,
                        template_type=item_data.get('clothing_type', 'Custom'),
                        name=profile_name,
                        unit="inches",
                        notes="Auto-saved from Order"
                    )
                    meas_repo.update_values(profile.id, {k: str(v) for k, v in measurements.items()})

            session.commit()
            logger.info(f"Order updated: {order.order_number}")
            return order

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update order: {e}")
            raise
        finally:
            session.close()

    def update_status(self, order_id: int, new_status: str) -> Order | None:
        """Change order status with transition validation."""
        session = get_session()
        try:
            order_repo = OrderRepository(session)
            order = order_repo.get_by_id(order_id)
            if not order:
                return None

            current = order.status
            if new_status not in VALID_TRANSITIONS.get(current, []):
                raise ValueError(
                    f"Cannot change status from {current} to {new_status}"
                )

            order = order_repo.update_status(order_id, new_status)
            session.commit()
            logger.info(f"Order {order.order_number} status: {current} → {new_status}")
            return order
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update order status: {e}")
            raise
        finally:
            session.close()

    def get_order(self, order_id: int) -> Order | None:
        session = get_session()
        try:
            return OrderRepository(session).get_by_id(order_id)
        finally:
            session.close()

    def mark_stage_complete(self, order_id: int, stage_name: str, worker_id: int, extra_amount: float = 0.0, extra_desc: str = "") -> Order:
        """Mark a specific stage (CUTTING or READY) as complete for an order by a worker."""
        session = get_session()
        try:
            order_repo = OrderRepository(session)
            order = order_repo.get_by_id(order_id)
            if not order:
                raise ValueError(f"Order {order_id} not found")
                
            from app.services.worker_service import worker_service
            
            # 1. Log WorkEntry for each item in the order
            for item in order.items:
                garment_label = f"{item.clothing_type} - {stage_name}"
                
                # Assign extra_amount only to the first item so we don't duplicate it
                amt = extra_amount if item == order.items[0] else 0.0
                desc = extra_desc if item == order.items[0] else None
                
                worker_service.submit_work_entry(
                    worker_id=worker_id,
                    garment_type=garment_label,
                    quantity=item.quantity,
                    bill_number=order.order_number,
                    extra_work_description=desc,
                    extra_amount=amt
                )
            
            new_status = "CUTTING_COMPLETE" if stage_name.upper() == "CUTTING" else "STITCHING_COMPLETE"
            logger.info(f"mark_stage_complete called for order {order_id} (current status: {order.status}) -> {new_status}")
            
            if new_status in VALID_TRANSITIONS.get(order.status, []):
                order = order_repo.update_status(order_id, new_status)
                logger.info("Transition valid, updated via order_repo.")
            elif order.status == new_status:
                logger.info("Already in this state.")
            else:
                # Force status update if invalid transition but worker completed it anyway
                logger.info(f"Invalid transition from {order.status} to {new_status}. Forcing update.")
                order = order_repo.update_status(order_id, new_status)
                
            # Pre-load customer details before commit
            customer_name = order.customer.name if order.customer else None
            customer_mobile = order.customer.mobile if order.customer else None
            order_number = order.order_number

            session.commit()
            
            # 3. Send WhatsApp if STITCHING_COMPLETE
            if new_status == "STITCHING_COMPLETE" and customer_mobile:
                from app.services.whatsapp_service import WhatsAppService
                try:
                    msg = (
                        f"✨ नमस्ते {customer_name}! ✨\n\n"
                        f"खुशखबरी! आपका ऑर्डर #{order_number} अब पूरी तरह से तैयार है।\n"
                        f"आप इसे हमारी दुकान से प्राप्त कर सकते हैं।\n\n"
                        f"धन्यवाद!"
                    )
                    wa = WhatsAppService()
                    wa.send_whatsapp_message(customer_mobile, msg)
                except Exception as wa_err:
                    logger.error(f"Failed to send WhatsApp ready message: {wa_err}")

            return order
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to mark stage complete: {e}")
            raise
        finally:
            session.close()

    def get_order_by_number(self, order_number: str) -> Order | None:
        session = get_session()
        try:
            return OrderRepository(session).get_by_order_number(order_number)
        finally:
            session.close()

    def get_all_orders(self, status: str = None) -> list[Order]:
        session = get_session()
        try:
            return OrderRepository(session).get_all(status)
        finally:
            session.close()

    def get_overdue_orders(self) -> list[Order]:
        session = get_session()
        try:
            return OrderRepository(session).get_overdue()
        finally:
            session.close()

    def get_dashboard_data(self, target_date: date = None) -> dict:
        """Get all data needed for the dashboard."""
        target_date = target_date or date.today()
        session = get_session()
        try:
            order_repo = OrderRepository(session)
            pay_repo = PaymentRepository(session)

            today_orders = order_repo.get_today_orders(target_date)
            # Today's Sales should be the money collected today (payments)
            today_sales = pay_repo.get_today_total(target_date)
            pending_payments = pay_repo.get_total_pending()
            today_deliveries = order_repo.get_by_delivery_date(target_date)
            status_counts = order_repo.count_by_status()
            
            # Sort recent orders by updated_at instead of created_at
            recent_orders = session.query(Order).options(
                joinedload(Order.customer),
                joinedload(Order.items),
            ).order_by(Order.updated_at.desc()).limit(5).all()
            
            overdue_orders = order_repo.get_overdue()
            urgent_not_started = order_repo.get_urgent_not_started(3)

            return {
                "orders_today": len(today_orders),
                "today_sales": today_sales,
                "pending_payments": pending_payments,
                "deliveries_today": len(today_deliveries),
                "today_deliveries_list": today_deliveries,
                "status_counts": status_counts,
                "recent_orders": recent_orders,
                "overdue_orders": overdue_orders,
                "urgent_not_started": urgent_not_started,
            }
        finally:
            session.close()
