from __future__ import annotations
"""Order service — order creation with measurement snapshot, status transitions."""

import os
import base64
import uuid
from datetime import date
from app.database.engine import get_session
from app.repositories.order_repo import OrderRepository
from app.repositories.measurement_repo import MeasurementRepository
from app.repositories.payment_repo import PaymentRepository
from app.models.order import Order
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Valid status transitions
VALID_TRANSITIONS = {
    "NEW": ["STITCHING", "READY", "DELIVERED", "CANCELLED"],
    "STITCHING": ["NEW", "READY", "DELIVERED", "CANCELLED"],
    "READY": ["NEW", "STITCHING", "DELIVERED", "CANCELLED"],
    "DELIVERED": ["READY", "CANCELLED"],  # Allow reverting if accidental
    "CANCELLED": ["NEW"],  # Allow reopening
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
            
            # Save to app/assets/www/uploads/items/
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            upload_dir = os.path.join(base_dir, "assets", "www", "uploads", "items")
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f:
                f.write(img_data)
                
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
                img_path = self._save_image(item_data.get('image_base64'))
                item = order_repo.add_item(
                    order_id=order.id,
                    clothing_type=item_data.get('clothing_type', 'Custom'),
                    quantity=item_data.get('quantity', 1),
                    price=item_data.get('price', 0.0),
                    image_path=img_path,
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
                img_path = self._save_image(item_data.get('image_base64'))
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
            today_sales = pay_repo.get_today_total(target_date)
            pending_payments = pay_repo.get_total_pending()
            today_deliveries = order_repo.get_by_delivery_date(target_date)
            status_counts = order_repo.count_by_status()
            recent_orders = order_repo.get_recent(5)
            overdue_orders = order_repo.get_overdue()

            return {
                "orders_today": len(today_orders),
                "today_sales": today_sales,
                "pending_payments": pending_payments,
                "deliveries_today": len(today_deliveries),
                "today_deliveries_list": today_deliveries,
                "status_counts": status_counts,
                "recent_orders": recent_orders,
                "overdue_orders": overdue_orders,
            }
        finally:
            session.close()
