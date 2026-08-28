from __future__ import annotations
"""Report printer — generates and prints business reports."""

from PySide6.QtWidgets import QWidget
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QPageSize
from PySide6.QtCore import Qt, QRectF, QPointF

from app.utils.formatters import format_currency, format_date_display
from app.utils.logger import get_logger

from app.printing.receipt_printer import _configure_thermal_printer, THERMAL_PRINTER_NAME, _make_fonts

logger = get_logger(__name__)


def print_report(report_data: dict, parent_widget: QWidget = None):
    """Print a business report from report data using a 58mm thermal layout."""
    from app.database.engine import get_session
    from app.repositories.settings_repo import SettingsRepository
    session = get_session()
    try:
        settings = SettingsRepository(session).get_settings()
        shop_name = settings.shop_name or "Tailor Shop"
        currency = settings.currency or "₹"
    finally:
        session.close()

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    _configure_thermal_printer(printer)
    printer.setPrinterName(THERMAL_PRINTER_NAME)

    dialog = QPrintDialog(printer, parent_widget)
    dialog.setWindowTitle("Print Report - POS58")
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

        def draw_metric(label, value, is_bold=False):
            nonlocal y
            painter.setFont(bold_font if is_bold else normal_font)
            painter.drawText(QRectF(margin, y, content_width * 0.6, 18),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label)
            painter.setFont(bold_font)
            painter.drawText(QRectF(margin + content_width * 0.5, y, content_width * 0.5, 18),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, value)
            y += 18

        # Title
        painter.setFont(title_font)
        painter.drawText(QRectF(margin, y, content_width, 24),
                         Qt.AlignmentFlag.AlignCenter, shop_name)
        y += 24
        
        painter.setFont(receipt_title_font)
        painter.drawText(QRectF(margin, y, content_width, 18),
                         Qt.AlignmentFlag.AlignCenter, "BUSINESS REPORT")
        y += 18

        draw_dashed_line()

        # Period
        painter.setFont(normal_font)
        start = report_data.get("start_date")
        end = report_data.get("end_date")
        painter.drawText(QRectF(margin, y, content_width, 18),
                         Qt.AlignmentFlag.AlignCenter, f"From: {format_date_display(start)}")
        y += 18
        painter.drawText(QRectF(margin, y, content_width, 18),
                         Qt.AlignmentFlag.AlignCenter, f"To: {format_date_display(end)}")
        y += 18

        draw_dashed_line()

        # Metrics
        draw_metric("Total Sales:", format_currency(report_data.get("total_sales", 0), currency))
        draw_metric("Total Orders:", str(report_data.get("total_orders", 0)))
        draw_metric("Completed:", str(report_data.get("completed_orders", 0)))

        draw_dashed_line()

        draw_metric("Payments Rcvd:", format_currency(report_data.get("total_payments", 0), currency))
        draw_metric("Pending Due:", format_currency(report_data.get("pending_payments", 0), currency))

        draw_dashed_line()

        draw_metric("Total Expenses:", format_currency(report_data.get("total_expenses", 0), currency))

        draw_dashed_line()

        draw_metric("EST. PROFIT:", format_currency(report_data.get("estimated_profit", 0), currency), is_bold=True)

        draw_dashed_line()

        # Footer
        y += 10
        painter.setFont(small_font)
        painter.drawText(QRectF(margin, y, content_width, 14),
                         Qt.AlignmentFlag.AlignCenter,
                         f"Generated by Tailor Shop Manager")
                         
        # Feed paper
        y += 80
        painter.setPen(QColor(255, 255, 255, 1))
        painter.drawText(QRectF(margin, y, 10, 10), Qt.AlignmentFlag.AlignLeft, ".")

    except Exception:
        logger.exception("Error while drawing business report")
        raise
    finally:
        painter.end()

    logger.info("Business report printed")
