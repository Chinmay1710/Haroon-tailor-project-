from __future__ import annotations
"""Stitching slip printer — generates a stitching slip with measurements for the workshop."""

from PySide6.QtWidgets import QWidget
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QPageSize
from PySide6.QtCore import Qt, QRectF, QPointF

from app.services.order_service import OrderService
from app.utils.formatters import format_date_display
from app.utils.logger import get_logger

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
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

    dialog = QPrintDialog(printer, parent_widget)
    dialog.setWindowTitle("Print Stitching Slip")
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

        title_font = QFont("Public Sans", 16, QFont.Weight.Bold)
        header_font = QFont("Public Sans", 12, QFont.Weight.Bold)
        normal_font = QFont("Public Sans", 10)
        large_font = QFont("Public Sans", 14, QFont.Weight.Bold)

        # Header
        painter.setFont(title_font)
        painter.setPen(QColor("#091426"))
        painter.drawText(QRectF(margin, y, content_width, 24),
                         Qt.AlignmentFlag.AlignCenter, f"{shop_name} — STITCHING SLIP")
        y += 35

        # Order info
        def draw_row(label, value):
            nonlocal y
            painter.setFont(normal_font)
            painter.setPen(QColor("#666666"))
            painter.drawText(QRectF(margin, y, content_width * 0.35, 18),
                             Qt.AlignmentFlag.AlignLeft, label)
            painter.setPen(QColor("#091426"))
            painter.drawText(QRectF(margin + content_width * 0.35, y, content_width * 0.65, 18),
                             Qt.AlignmentFlag.AlignLeft, value)
            y += 20

        draw_row("Order Number:", order.order_number)
        draw_row("Customer:", order.customer.name if order.customer else "—")
        draw_row("Order Date:", format_date_display(order.order_date))
        draw_row("Delivery Date:", format_date_display(order.delivery_date))

        y += 10
        painter.setPen(QPen(QColor("#091426"), 2))
        painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
        y += 15

        # For each item
        for item in (order.items or []):
            painter.setFont(large_font)
            painter.setPen(QColor("#091426"))
            painter.drawText(QRectF(margin, y, content_width, 22),
                             Qt.AlignmentFlag.AlignLeft,
                             f"{item.clothing_type} × {item.quantity}")
            y += 30

            # Measurements
            if item.measurements:
                painter.setFont(header_font)
                painter.drawText(QRectF(margin, y, content_width, 18),
                                 Qt.AlignmentFlag.AlignLeft, "Measurements:")
                y += 22

                col_width = content_width / 3
                col = 0
                for m in item.measurements:
                    x = margin + col * col_width
                    painter.setFont(normal_font)
                    painter.setPen(QColor("#666666"))
                    painter.drawText(QRectF(x, y, col_width, 16),
                                     Qt.AlignmentFlag.AlignLeft,
                                     f"{m.field_name}:")
                    painter.setPen(QColor("#091426"))
                    painter.setFont(QFont("Public Sans", 11, QFont.Weight.Bold))
                    painter.drawText(QRectF(x, y + 16, col_width, 18),
                                     Qt.AlignmentFlag.AlignLeft,
                                     f"{m.field_value} {m.unit}")
                    col += 1
                    if col >= 3:
                        col = 0
                        y += 38
                if col > 0:
                    y += 38
            else:
                painter.setFont(normal_font)
                painter.setPen(QColor("#999999"))
                painter.drawText(QRectF(margin, y, content_width, 18),
                                 Qt.AlignmentFlag.AlignLeft, "No measurements recorded")
                y += 22

            y += 10
            painter.setPen(QPen(QColor("#cccccc"), 1))
            painter.drawLine(QPointF(margin, y), QPointF(width - margin, y))
            y += 15

        # Special instructions
        if order.special_instructions:
            painter.setFont(header_font)
            painter.setPen(QColor("#091426"))
            painter.drawText(QRectF(margin, y, content_width, 18),
                             Qt.AlignmentFlag.AlignLeft, "SPECIAL INSTRUCTIONS:")
            y += 22
            painter.setFont(QFont("Public Sans", 11))
            painter.setPen(QColor("#333333"))
            painter.drawText(QRectF(margin, y, content_width, 80),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.TextWordWrap,
                             order.special_instructions)
            y += 60

        # Status
        y += 20
        painter.setFont(large_font)
        painter.setPen(QColor("#091426"))
        painter.drawText(QRectF(margin, y, content_width, 22),
                         Qt.AlignmentFlag.AlignLeft,
                         f"Status: {order.status}")

    finally:
        painter.end()

    logger.info(f"Stitching slip printed for order {order.order_number}")
