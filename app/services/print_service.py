import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A5
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from app.database.engine import get_session
from app.repositories.order_repo import OrderRepository
from app.repositories.payment_repo import PaymentRepository
from app.repositories.settings_repo import SettingsRepository

class PrintService:
    def __init__(self, session=None):
        self._session = session
        
    def _get_session(self):
        if self._session: return self._session
        return get_session()
        
    def _get_settings(self, session):
        repo = SettingsRepository(session)
        settings = repo.get_settings()
        return {
            "shop_name": settings.shop_name,
            "currency_symbol": settings.currency
        }

    def generate_receipt_pdf(self, order_id: int, output_path: str) -> str:
        session = self._get_session()
        try:
            order = OrderRepository(session).get_by_id(order_id)
            if not order:
                raise ValueError("Order not found")
                
            settings = self._get_settings(session)
            shop_name = settings.get("shop_name", "Artisan Stitch")
            currency = settings.get("currency_symbol", "₹")
            
            c = canvas.Canvas(output_path, pagesize=A5)
            width, height = A5
            
            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2.0, height - 40, shop_name)
            c.setFont("Helvetica", 10)
            c.drawCentredString(width/2.0, height - 55, "Customer Receipt")
            
            # Order details
            c.setFont("Helvetica", 12)
            c.drawString(40, height - 90, f"Order Number: {order.order_number}")
            c.drawString(40, height - 105, f"Date: {order.order_date.isoformat() if order.order_date else ''}")
            if order.customer:
                c.drawString(40, height - 120, f"Customer: {order.customer.name}")
                c.drawString(40, height - 135, f"Mobile: {order.customer.mobile}")
                
            # Amounts
            c.drawString(40, height - 165, f"Total Amount: {currency}{order.total_amount}")
            c.drawString(40, height - 180, f"Advance: {currency}{order.advance_amount}")
            c.drawString(40, height - 195, f"Paid: {currency}{order.paid_amount}")
            
            # Remaining
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, height - 215, f"Balance Due: {currency}{order.remaining_amount}")
            
            c.setFont("Helvetica", 12)
            c.drawString(40, height - 240, f"Delivery Date: {order.delivery_date.isoformat() if order.delivery_date else 'Not set'}")
            
            c.showPage()
            c.save()
            return output_path
        finally:
            if not self._session:
                session.close()

    def generate_stitching_slip(self, order_id: int, output_path: str) -> str:
        session = self._get_session()
        try:
            order = OrderRepository(session).get_by_id(order_id)
            if not order:
                raise ValueError("Order not found")
                
            settings = self._get_settings(session)
            shop_name = settings.get("shop_name", "Artisan Stitch")
            
            c = canvas.Canvas(output_path, pagesize=A5)
            width, height = A5
            
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2.0, height - 40, shop_name)
            c.setFont("Helvetica", 10)
            c.drawCentredString(width/2.0, height - 55, "Stitching Slip (Internal)")
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, height - 90, f"Order: {order.order_number}")
            c.setFont("Helvetica", 12)
            c.drawString(40, height - 110, f"Instructions: {order.special_instructions}")
            
            # Print items and measurements
            y = height - 140
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Measurements:")
            y -= 20
            c.setFont("Helvetica", 10)
            
            for item in order.items:
                c.drawString(40, y, f"Item: {item.clothing_type}")
                y -= 15
                for snap in item.measurements:
                    c.drawString(50, y, f"{snap.field_name}: {snap.field_value} {snap.unit}")
                    y -= 15
                    if y < 150:
                        c.showPage()
                        y = height - 50

            # --- ADD QR CODE ---
            try:
                import qrcode
                from reportlab.lib.utils import ImageReader
                from app.web.tunnel import GLOBAL_TUNNEL_URL
                import tempfile

                # We now just encode "ORDER:{id}" so the in-app scanner can parse it.
                scan_url = f"ORDER:{order.id}"

                qr = qrcode.QRCode(version=1, box_size=3, border=1)
                qr.add_data(scan_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                    img.save(tf.name)
                    qr_path = tf.name

                qr_size = 80
                qr_y = 50
                if y < (qr_y + qr_size + 20):
                    c.showPage()
                    qr_y = height - qr_size - 40

                c.drawImage(ImageReader(qr_path), width/2.0 - qr_size/2, qr_y, width=qr_size, height=qr_size)
                c.setFont("Helvetica", 8)
                c.drawCentredString(width/2.0, qr_y - 10, "Scan to update status")
                os.remove(qr_path)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to generate QR code: {e}")

            c.showPage()
            c.save()
            return output_path
        finally:
            if not self._session:
                session.close()
