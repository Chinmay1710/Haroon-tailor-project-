from __future__ import annotations
"""Stitching slip printer — generates a stitching slip with measurements for the workshop."""

from PySide6.QtWidgets import QWidget
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QPageSize, QImage
from PySide6.QtCore import Qt, QRectF, QPointF

from app.services.order_service import OrderService
from app.utils.formatters import format_date_display
from app.utils.logger import get_logger

# Import thermal printer utilities from receipt_printer
from app.printing.receipt_printer import _configure_thermal_printer, THERMAL_PRINTER_NAME, _make_fonts

import qrcode
from io import BytesIO

logger = get_logger(__name__)


def print_stitching_slip(order_id: int, parent_widget: QWidget = None):
    """Generate and print a stitching slip with measurements."""
    order = OrderService().get_order(order_id)
    if not order:
        logger.error(f"Order {order_id} not found for slip printing")
        return

    from app.database.engine import get_session
    from app.repositories.settings_repo import SettingsRepository
    session = get_session()
    try:
        settings = SettingsRepository(session).get_settings()
        shop_name = settings.shop_name or "Tailor Shop"
    finally:
        session.close()

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    _configure_thermal_printer(printer)
    printer.setPrinterName(THERMAL_PRINTER_NAME)

    dialog = QPrintDialog(printer, parent_widget)
    dialog.setWindowTitle("Print Stitching Slip")
    if dialog.exec() != QPrintDialog.DialogCode.Accepted:
        return

    _configure_thermal_printer(printer)

    painter = QPainter()
    if not painter.begin(printer):
        logger.error("Failed to start printing")
        return

    try:
        device_rect = printer.paperRect(QPrinter.Unit.DevicePixel)
        point_rect = printer.paperRect(QPrinter.Unit.Point)
        
        scale = 384.0 / max(1.0, point_rect.width())
        painter.scale(scale, scale)

        width = point_rect.width()
        margin = 12.0
        content_width = width - (2.0 * margin)
        y = 5.0

        (
            title_font,
            shop_detail_font,
            receipt_title_font,
            normal_font,
            value_font,
            bold_font,
            small_font,
        ) = _make_fonts(scale)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)

        def draw_dashed_line():
            nonlocal y
            y += 5
            pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
            y += 5

        def draw_row(left: str, right: str, font_left=normal_font, font_right=normal_font, right_bold=False):
            nonlocal y
            painter.setFont(font_left)
            painter.drawText(
                QRectF(margin, y, content_width * 0.5, 18),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                left
            )
            painter.setFont(bold_font if right_bold else font_right)
            painter.drawText(
                QRectF(margin + content_width * 0.4, y, content_width * 0.6, 18),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                right
            )
            y += 18

        # 1. STITCHING SLIP Title
        painter.setFont(title_font)
        painter.drawText(
            QRectF(margin, y, content_width, 24),
            Qt.AlignmentFlag.AlignCenter,
            "STITCHING SLIP"
        )
        y += 24

        # 2. Shop Name
        painter.setFont(shop_detail_font)
        painter.drawText(
            QRectF(margin, y, content_width, 14),
            Qt.AlignmentFlag.AlignCenter,
            shop_name
        )
        y += 14

        draw_dashed_line()

        # 3. Order Details
        draw_row("Order No:", order.order_number, font_left=bold_font, right_bold=True)
        draw_row("Due:", format_date_display(order.delivery_date))

        draw_dashed_line()

        # 4. Customer
        customer_name = order.customer.name if order.customer else "Walk-in"
        painter.setFont(normal_font)
        painter.drawText(QRectF(margin, y, content_width * 0.35, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Customer:")
        painter.setFont(bold_font)
        painter.drawText(QRectF(margin + content_width * 0.35, y, content_width * 0.65, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, customer_name)
        y += 18

        draw_dashed_line()

        # 5. Garments
        painter.setFont(bold_font)
        painter.drawText(QRectF(margin, y, content_width, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Garments:")
        y += 18
        painter.setFont(normal_font)
        for item in (order.items or []):
            painter.drawText(QRectF(margin, y, content_width, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{item.clothing_type} (x{item.quantity})")
            y += 18

        draw_dashed_line()

        # 6. Measurements
        painter.setFont(bold_font)
        painter.drawText(QRectF(margin, y, content_width, 18), Qt.AlignmentFlag.AlignCenter, "MEASUREMENTS")
        y += 22

        for item in (order.items or []):
            if item.measurements:
                painter.setFont(bold_font)
                painter.drawText(QRectF(margin, y, content_width, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{item.clothing_type}")
                
                # underline it
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(item.clothing_type)
                painter.drawLine(QPointF(margin, y + 16), QPointF(margin + tw, y + 16))
                
                y += 18
                
                for m in item.measurements:
                    draw_row(f"{m.field_name}:", f"{m.field_value}\"", font_right=bold_font)
                
                y += 5

        draw_dashed_line()

        # 7. Cut / Sewn By
        y += 5
        painter.setFont(normal_font)
        painter.drawText(QRectF(margin, y, content_width * 0.5, 18), Qt.AlignmentFlag.AlignLeft, "Cut By: _______")
        painter.drawText(QRectF(margin + content_width * 0.5, y, content_width * 0.5, 18), Qt.AlignmentFlag.AlignRight, "Sewn By: _______")
        y += 25

        # 8. QR Code
        qr_size = int(content_width * 0.5)
        qr_x = margin + (content_width - qr_size) / 2
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(f"haroon-tailor://order/{order.order_number}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to QImage
        buf = BytesIO()
        img.save(buf, format="PNG")
        qimg = QImage.fromData(buf.getvalue())
        
        painter.drawImage(QRectF(qr_x, y, qr_size, qr_size), qimg)
        y += qr_size + 10

        # Scan text
        painter.setFont(small_font)
        painter.drawText(QRectF(margin, y, content_width, 14), Qt.AlignmentFlag.AlignCenter, "Scan to Update Status")
        y += 14

        # Generated date
        from datetime import datetime
        now_str = datetime.now().strftime("%d %b %Y - %I:%M:%S %p")
        painter.drawText(QRectF(margin, y, content_width, 14), Qt.AlignmentFlag.AlignCenter, f"Generated: {now_str}")
        y += 14

        # Fix for printer stopping early: feed paper by drawing blank space at the bottom
        y += 80
        painter.setPen(QColor(255, 255, 255, 1)) # practically invisible
        painter.drawText(QRectF(margin, y, 10, 10), Qt.AlignmentFlag.AlignLeft, ".")

    except Exception:
        logger.exception(f"Error while drawing stitching slip for order {order.order_number}")
        raise

    finally:
        painter.end()

    logger.info(f"Stitching slip printed for order {order.order_number}")
