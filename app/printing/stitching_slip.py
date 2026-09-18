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

    # We use 1 copy because we manually iterate and page each item
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
        
        scale = 576.0 / max(1.0, point_rect.width())
        painter.scale(scale, scale)

        width = point_rect.width()
        margin = 12.0
        content_width = width - (2.0 * margin)
        
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

        for item_idx, item in enumerate(order.items or []):
            if item_idx > 0:
                printer.newPage()
                # Add top margin to account for cutter-to-printhead physical distance 
                # which Windows drivers often ignore on newPage().
                y = 70.0
            else:
                y = 5.0
            
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
            from datetime import datetime
            draw_row("Bill No:", order.order_number or "", font_left=bold_font, right_bold=True)
            draw_row("Due:", format_date_display(order.delivery_date))
            draw_row("Time:", datetime.now().strftime("%I:%M %p"))

            draw_dashed_line()

            # 4. Customer
            customer_name = order.customer.name if order.customer else "Walk-in"
            painter.setFont(normal_font)
            painter.drawText(QRectF(margin, y, content_width * 0.35, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Customer:")
            painter.setFont(bold_font)
            painter.drawText(QRectF(margin + content_width * 0.35, y, content_width * 0.65, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, customer_name)
            y += 18

            draw_dashed_line()

            # 5. Garment (This item only)
            painter.setFont(bold_font)
            painter.drawText(QRectF(margin, y, content_width, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Garment:")
            y += 18
            painter.setFont(normal_font)
            painter.drawText(QRectF(margin, y, content_width, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{item.clothing_type} (x{item.quantity})")
            y += 18

            draw_dashed_line()

            # Instructions / Notes
            instructions = []
            if item.notes:
                instructions.append(f"Item Note: {item.notes}")
                
            if instructions:
                painter.setFont(bold_font)
                painter.drawText(QRectF(margin, y, content_width, 18), Qt.AlignmentFlag.AlignCenter, "INSTRUCTIONS")
                y += 22
                
                painter.setFont(normal_font)
                text = "\n".join(instructions)
                
                rect = painter.boundingRect(QRectF(margin, y, content_width, 2000), Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, text)
                
                painter.drawText(QRectF(margin, y, content_width, rect.height()), Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, text)
                
                y += rect.height() + 10
                
                draw_dashed_line()

            # 6. Measurements
            painter.setFont(bold_font)
            painter.drawText(QRectF(margin, y, content_width, 18), Qt.AlignmentFlag.AlignCenter, "MEASUREMENTS")
            y += 22

            if item.measurements:
                painter.setFont(bold_font)
                clothing_text = f"{item.clothing_type} - {order.order_number or ''}"
                painter.drawText(QRectF(margin, y, content_width, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, clothing_text)
                
                # underline it
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(clothing_text)
                painter.drawLine(QPointF(margin, y + 16), QPointF(margin + tw, y + 16))
                
                y += 18
                
                new_cols = 4
                new_rows = 6
                col_width = content_width / new_cols
                
                painter.setPen(QPen(QColor("#000000"), 1.0))
                
                meas_dict = {str(m.field_name): str(m.field_value) for m in item.measurements}
                
                meas_val_font = QFont("Arial")
                meas_val_font.setPointSizeF(14.0 / scale)
                meas_val_font.setWeight(QFont.Weight.Normal)
                
                painter.setFont(meas_val_font)
                fm = painter.fontMetrics()
                
                for r in range(new_rows):
                    max_text_width = 45 # Minimum height for the row
                    for c in range(new_cols):
                        orig_row = 3 - c
                        orig_col = r
                        orig_idx = orig_row * 6 + orig_col
                        box_number = orig_idx + 1
                        val = str(meas_dict.get(f"Box {box_number}", "")).strip()
                        if val:
                            w = fm.horizontalAdvance(val) + 16 # 8px padding
                            if w > max_text_width:
                                max_text_width = w
                                
                    row_height = max_text_width
                    
                    for c in range(new_cols):
                        orig_row = 3 - c
                        orig_col = r
                        orig_idx = orig_row * 6 + orig_col
                        box_number = orig_idx + 1
                        
                        x = margin + c * col_width
                        y_cell = y
                        
                        val = str(meas_dict.get(f"Box {box_number}", "")).strip()
                        
                        painter.drawRect(QRectF(x, y_cell, col_width, row_height))
                        
                        if val != "":
                            painter.save()
                            painter.translate(x + col_width / 2, y_cell + row_height / 2)
                            painter.rotate(90)
                            # Swapped width and height because of 90 deg rotation
                            painter.drawText(QRectF(-row_height / 2, -col_width / 2, row_height, col_width), Qt.AlignmentFlag.AlignCenter, val)
                            painter.restore()
                            
                    y += row_height
                painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
                y += 6

            draw_dashed_line()

            # 7. Cut / Sewn By
            y += 5
            painter.setFont(normal_font)
            painter.drawText(QRectF(margin, y, content_width * 0.5, 18), Qt.AlignmentFlag.AlignLeft, "Cut By: _______")
            painter.drawText(QRectF(margin + content_width * 0.5, y, content_width * 0.5, 18), Qt.AlignmentFlag.AlignRight, "Sewn By: _______")
            y += 25

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
