from __future__ import annotations
"""Receipt printer — generates and prints customer receipts using Qt printing."""

from PySide6.QtWidgets import QWidget
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QPageSize
from PySide6.QtCore import Qt, QRectF, QPointF

from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.utils.formatters import format_currency, format_date_display
from app.utils.logger import get_logger

logger = get_logger(__name__)


def print_customer_receipt(order_id: int, parent_widget: QWidget = None):
    """Generate and print a customer receipt for the given order."""
    order_service = OrderService()
    payment_service = PaymentService()

    order = order_service.get_order(order_id)
    if not order:
        logger.error(f"Order {order_id} not found for receipt printing")
        return

    # Get shop settings
    from app.database.engine import get_session
    from app.repositories.settings_repo import SettingsRepository
    session = get_session()
    try:
        settings = SettingsRepository(session).get_settings()
        shop_name = settings.shop_name or "Tailor Shop"
        shop_phone = settings.phone or ""
        shop_address = settings.address or ""
        currency = settings.currency or "₹"
    finally:
        session.close()

    payments = payment_service.get_payments_for_order(order_id)

    # Create printer
    printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

    dialog = QPrintDialog(printer, parent_widget)
    dialog.setWindowTitle("Print Receipt")
    if dialog.exec() != QPrintDialog.DialogCode.Accepted:
        return

    painter = QPainter()
    if not painter.begin(printer):
        logger.error("Failed to start printing")
        return

    try:
        page_rect = printer.pageRect(QPrinter.Unit.Point)
        width = page_rect.width()
        margin = 40
        content_width = width - 2 * margin
        y = margin

        # ─── Header ───
        title_font = QFont("Public Sans", 18, QFont.Weight.Bold)
        normal_font = QFont("Public Sans", 10)
        small_font = QFont("Public Sans", 8)
        header_font = QFont("Public Sans", 12, QFont.Weight.Bold)
        value_font = QFont("Public Sans", 11)

        # Shop name
        painter.setFont(title_font)
        painter.setPen(QColor("#091426"))
        painter.drawText(QRectF(margin, y, content_width, 30),
                         Qt.AlignmentFlag.AlignCenter, shop_name)
        y += 30

        # Shop details
        painter.setFont(small_font)
        painter.setPen(QColor("#666666"))
        if shop_address:
            painter.drawText(QRectF(margin, y, content_width, 16),
                             Qt.AlignmentFlag.AlignCenter, shop_address)
            y += 16
        if shop_phone:
            painter.drawText(QRectF(margin, y, content_width, 16),
                             Qt.AlignmentFlag.AlignCenter, f"Phone: {shop_phone}")
            y += 16

        y += 10

        # Divider
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        # Receipt title
        painter.setFont(header_font)
        painter.setPen(QColor("#091426"))
        painter.drawText(QRectF(margin, y, content_width, 20),
                         Qt.AlignmentFlag.AlignCenter, "CUSTOMER RECEIPT")
        y += 30

        # Order details
        def draw_row(label: str, value: str, bold_value: bool = False):
            nonlocal y
            painter.setFont(normal_font)
            painter.setPen(QColor("#666666"))
            painter.drawText(QRectF(margin, y, content_width * 0.4, 18),
                             Qt.AlignmentFlag.AlignLeft, label)
            painter.setFont(value_font if bold_value else normal_font)
            painter.setPen(QColor("#091426"))
            painter.drawText(QRectF(margin + content_width * 0.4, y, content_width * 0.6, 18),
                             Qt.AlignmentFlag.AlignLeft, value)
            y += 20

        draw_row("Order Number:", order.order_number)
        draw_row("Date:", format_date_display(order.order_date))
        draw_row("Customer:", order.customer.name if order.customer else "—")
        if order.customer and order.customer.mobile:
            draw_row("Mobile:", order.customer.mobile)
        draw_row("Delivery Date:", format_date_display(order.delivery_date))

        y += 10
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        # Items
        painter.setFont(header_font)
        painter.setPen(QColor("#091426"))
        painter.drawText(QRectF(margin, y, content_width, 20),
                         Qt.AlignmentFlag.AlignLeft, "Items")
        y += 25

        for item in (order.items or []):
            draw_row(f"  {item.clothing_type} × {item.quantity}",
                     format_currency(item.price * item.quantity, currency))

        y += 10
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        # Payment summary
        draw_row("Total Amount:", format_currency(order.total_amount, currency), bold_value=True)
        draw_row("Paid:", format_currency(order.paid_amount, currency))
        draw_row("Remaining:", format_currency(order.remaining_amount, currency), bold_value=True)

        y += 10
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        # Payment history
        if payments:
            painter.setFont(header_font)
            painter.setPen(QColor("#091426"))
            painter.drawText(QRectF(margin, y, content_width, 20),
                             Qt.AlignmentFlag.AlignLeft, "Payment History")
            y += 25

            for p in payments:
                draw_row(
                    f"  {format_date_display(p.payment_date)} ({p.payment_method})",
                    format_currency(p.amount, currency))

        y += 20

        # Special instructions
        if order.special_instructions:
            painter.setFont(header_font)
            painter.setPen(QColor("#091426"))
            painter.drawText(QRectF(margin, y, content_width, 20),
                             Qt.AlignmentFlag.AlignLeft, "Special Instructions")
            y += 22
            painter.setFont(normal_font)
            painter.setPen(QColor("#666666"))
            painter.drawText(QRectF(margin, y, content_width, 60),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.TextWordWrap,
                             order.special_instructions)
            y += 50

        # Footer
        y += 20
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        painter.setFont(small_font)
        painter.setPen(QColor("#999999"))
        painter.drawText(QRectF(margin, y, content_width, 14),
                         Qt.AlignmentFlag.AlignCenter, "Thank you for your business!")
        y += 14
        painter.drawText(QRectF(margin, y, content_width, 14),
                         Qt.AlignmentFlag.AlignCenter,
                         f"Generated by {shop_name} — Tailor Shop Manager")

    finally:
        painter.end()

    logger.info(f"Receipt printed for order {order.order_number}")

def generate_receipt_pdf(order_id: int, output_path: str) -> bool:
    """Generate a customer receipt as a PDF file silently."""
    order_service = OrderService()
    payment_service = PaymentService()

    order = order_service.get_order(order_id)
    if not order:
        logger.error(f"Order {order_id} not found for PDF generation")
        return False

    # Get shop settings
    from app.database.engine import get_session
    from app.repositories.settings_repo import SettingsRepository
    session = get_session()
    try:
        settings = SettingsRepository(session).get_settings()
        shop_name = settings.shop_name or "Tailor Shop"
        shop_phone = settings.phone or ""
        shop_address = settings.address or ""
        currency = settings.currency or "₹"
    finally:
        session.close()

    payments = payment_service.get_payments_for_order(order_id)

    # Create printer
    printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(output_path)

    painter = QPainter()
    if not painter.begin(printer):
        logger.error("Failed to start printing to PDF")
        return False

    try:
        page_rect = printer.pageRect(QPrinter.Unit.Point)
        width = page_rect.width()
        margin = 40
        content_width = width - 2 * margin
        y = margin

        # ─── Header ───
        title_font = QFont("Public Sans", 18, QFont.Weight.Bold)
        normal_font = QFont("Public Sans", 10)
        small_font = QFont("Public Sans", 8)
        header_font = QFont("Public Sans", 12, QFont.Weight.Bold)
        value_font = QFont("Public Sans", 11)

        # Shop name
        painter.setFont(title_font)
        painter.setPen(QColor("#091426"))
        painter.drawText(QRectF(margin, y, content_width, 30),
                         Qt.AlignmentFlag.AlignCenter, shop_name)
        y += 30

        # Shop details
        painter.setFont(small_font)
        painter.setPen(QColor("#666666"))
        if shop_address:
            painter.drawText(QRectF(margin, y, content_width, 16),
                             Qt.AlignmentFlag.AlignCenter, shop_address)
            y += 16
        if shop_phone:
            painter.drawText(QRectF(margin, y, content_width, 16),
                             Qt.AlignmentFlag.AlignCenter, f"Phone: {shop_phone}")
            y += 16

        y += 10

        # Divider
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        # Receipt title
        painter.setFont(header_font)
        painter.setPen(QColor("#091426"))
        painter.drawText(QRectF(margin, y, content_width, 20),
                         Qt.AlignmentFlag.AlignCenter, "CUSTOMER RECEIPT")
        y += 30

        # Order details
        def draw_row(label: str, value: str, bold_value: bool = False):
            nonlocal y
            painter.setFont(normal_font)
            painter.setPen(QColor("#666666"))
            painter.drawText(QRectF(margin, y, content_width * 0.4, 18),
                             Qt.AlignmentFlag.AlignLeft, label)
            painter.setFont(value_font if bold_value else normal_font)
            painter.setPen(QColor("#091426"))
            painter.drawText(QRectF(margin + content_width * 0.4, y, content_width * 0.6, 18),
                             Qt.AlignmentFlag.AlignLeft, value)
            y += 20

        draw_row("Order Number:", order.order_number)
        draw_row("Date:", format_date_display(order.order_date))
        draw_row("Customer:", order.customer.name if order.customer else "—")
        if order.customer and order.customer.mobile:
            draw_row("Mobile:", order.customer.mobile)
        draw_row("Delivery Date:", format_date_display(order.delivery_date))

        y += 10
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        # Items
        painter.setFont(header_font)
        painter.setPen(QColor("#091426"))
        painter.drawText(QRectF(margin, y, content_width, 20),
                         Qt.AlignmentFlag.AlignLeft, "Items")
        y += 25

        for item in (order.items or []):
            draw_row(f"  {item.clothing_type} × {item.quantity}",
                     format_currency(item.price * item.quantity, currency))

        y += 10
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        # Payment summary
        draw_row("Total Amount:", format_currency(order.total_amount, currency), bold_value=True)
        draw_row("Paid:", format_currency(order.paid_amount, currency))
        draw_row("Remaining:", format_currency(order.remaining_amount, currency), bold_value=True)

        y += 10
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        # Payment history
        if payments:
            painter.setFont(header_font)
            painter.setPen(QColor("#091426"))
            painter.drawText(QRectF(margin, y, content_width, 20),
                             Qt.AlignmentFlag.AlignLeft, "Payment History")
            y += 25

            for p in payments:
                draw_row(
                    f"  {format_date_display(p.payment_date)} ({p.payment_method})",
                    format_currency(p.amount, currency))

        y += 20

        # Special instructions
        if order.special_instructions:
            painter.setFont(header_font)
            painter.setPen(QColor("#091426"))
            painter.drawText(QRectF(margin, y, content_width, 20),
                             Qt.AlignmentFlag.AlignLeft, "Special Instructions")
            y += 22
            painter.setFont(normal_font)
            painter.setPen(QColor("#666666"))
            painter.drawText(QRectF(margin, y, content_width, 60),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.TextWordWrap,
                             order.special_instructions)
            y += 50

        # Footer
        y += 20
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        painter.setFont(small_font)
        painter.setPen(QColor("#999999"))
        painter.drawText(QRectF(margin, y, content_width, 14),
                         Qt.AlignmentFlag.AlignCenter, "Thank you for your business!")
        y += 14
        painter.drawText(QRectF(margin, y, content_width, 14),
                         Qt.AlignmentFlag.AlignCenter,
                         f"Generated by {shop_name} — Tailor Shop Manager")

    finally:
        painter.end()

    logger.info(f"Receipt PDF generated for order {order.order_number} at {output_path}")
    return True
