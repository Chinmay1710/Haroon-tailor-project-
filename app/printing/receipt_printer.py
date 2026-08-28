from __future__ import annotations

"""Receipt printer — generates and prints customer receipts using Qt printing.

The customer receipt is formatted specifically for 58mm thermal POS printers.
PDF generation remains A4 and is kept separate from thermal printing.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import (
    QPainter,
    QFont,
    QColor,
    QPen,
    QPageSize,
)
from PySide6.QtCore import Qt, QRectF, QPointF, QSizeF

from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.utils.formatters import format_currency, format_date_display
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Thermal printer configuration
# ---------------------------------------------------------------------------

THERMAL_PRINTER_NAME = "POS58 Printer"

# 58mm paper.
# A height of 250mm gives enough room for a normal tailor receipt while
# allowing the Windows thermal printer driver to handle the roll.
THERMAL_PAPER_WIDTH_MM = 58.0
THERMAL_PAPER_HEIGHT_MM = 250.0

# Small thermal-printer margins.
THERMAL_MARGIN_MM = 3.0


def _configure_thermal_printer(printer: QPrinter) -> None:
    """Configure a QPrinter for a 58mm thermal POS printer."""

    # High resolution is generally more appropriate for thermal printers.
    printer.setResolution(203)

    # 58mm x 250mm custom page.
    page_size = QPageSize(
        QSizeF(
            THERMAL_PAPER_WIDTH_MM,
            THERMAL_PAPER_HEIGHT_MM,
        ),
        QPageSize.Unit.Millimeter,
        "POS58 Receipt",
    )

    printer.setPageSize(page_size)

    # Keep the printable content inside a small margin.
    printer.setPageMargins(
        THERMAL_MARGIN_MM,
        THERMAL_MARGIN_MM,
        THERMAL_MARGIN_MM,
        THERMAL_MARGIN_MM,
        QPrinter.Unit.Millimeter,
    )

    # Use color mode even though the thermal printer is monochrome.
    printer.setColorMode(QPrinter.ColorMode.GrayScale)

    # One copy.
    printer.setCopyCount(1)


def _make_fonts():
    """Create fonts suitable for a 58mm thermal receipt."""

    # Fonts are intentionally smaller than the previous A4 implementation.
    #
    # Arial is commonly available on Windows and gives reasonable fallback
    # support for Indian-language characters.
    title_font = QFont("Arial", 13, QFont.Weight.Bold)
    shop_detail_font = QFont("Arial", 7)
    receipt_title_font = QFont("Arial", 9, QFont.Weight.Bold)

    normal_font = QFont("Arial", 7)
    value_font = QFont("Arial", 7)

    bold_font = QFont("Arial", 7, QFont.Weight.Bold)
    small_font = QFont("Arial", 6)

    return (
        title_font,
        shop_detail_font,
        receipt_title_font,
        normal_font,
        value_font,
        bold_font,
        small_font,
    )


def _draw_centered_text(
    painter: QPainter,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
) -> None:
    """Draw centered single-line text."""

    painter.drawText(
        QRectF(x, y, width, height),
        Qt.AlignmentFlag.AlignCenter,
        str(text),
    )


def _draw_left_text(
    painter: QPainter,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
) -> None:
    """Draw left-aligned single-line text."""

    painter.drawText(
        QRectF(x, y, width, height),
        Qt.AlignmentFlag.AlignLeft
        | Qt.AlignmentFlag.AlignVCenter,
        str(text),
    )


def _draw_right_text(
    painter: QPainter,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
) -> None:
    """Draw right-aligned single-line text."""

    painter.drawText(
        QRectF(x, y, width, height),
        Qt.AlignmentFlag.AlignRight
        | Qt.AlignmentFlag.AlignVCenter,
        str(text),
    )


def _draw_divider(
    painter: QPainter,
    x1: float,
    x2: float,
    y: float,
) -> None:
    """Draw a thermal-receipt divider."""

    painter.setPen(QPen(QColor("#000000"), 0.7))
    painter.drawLine(
        QPointF(x1, y),
        QPointF(x2, y),
    )


def _draw_wrapped_text(
    painter: QPainter,
    text: str,
    rect: QRectF,
) -> float:
    """Draw wrapped text and return approximate height consumed."""

    if not text:
        return 0.0

    painter.drawText(
        rect,
        Qt.AlignmentFlag.AlignLeft
        | Qt.AlignmentFlag.TextWordWrap,
        str(text),
    )

    # Estimate the consumed height.
    # This is intentionally conservative for thermal printing.
    lines = max(
        1,
        len(str(text)) // max(1, int(rect.width() / 4.0)) + 1,
    )

    return min(
        rect.height(),
        lines * 9.0,
    )


def _draw_thermal_receipt(
    painter: QPainter,
    printer: QPrinter,
    order,
    payments,
    shop_name: str,
    shop_phone: str,
    shop_address: str,
    currency: str,
) -> None:
    """Draw the complete receipt using a 58mm thermal layout."""

    page_rect = printer.pageRect(QPrinter.Unit.Point)

    width = page_rect.width()

    # Work inside the printer's printable page.
    margin = max(
        6.0,
        width * (THERMAL_MARGIN_MM / THERMAL_PAPER_WIDTH_MM),
    )

    content_width = width - (2.0 * margin)

    y = 4.0

    # -----------------------------------------------------------------------
    # Fonts
    # -----------------------------------------------------------------------

    (
        title_font,
        shop_detail_font,
        receipt_title_font,
        normal_font,
        value_font,
        bold_font,
        small_font,
    ) = _make_fonts()

    # -----------------------------------------------------------------------
    # General painter configuration
    # -----------------------------------------------------------------------

    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
    painter.setPen(QColor("#000000"))

    # -----------------------------------------------------------------------
    # Shop header
    # -----------------------------------------------------------------------

    painter.setFont(title_font)

    _draw_centered_text(
        painter,
        margin,
        y,
        content_width,
        22,
        shop_name,
    )

    y += 23

    painter.setFont(shop_detail_font)

    if shop_address:
        # Address may be longer than one line.
        address_rect = QRectF(
            margin,
            y,
            content_width,
            22,
        )

        painter.drawText(
            address_rect,
            Qt.AlignmentFlag.AlignCenter
            | Qt.AlignmentFlag.TextWordWrap,
            str(shop_address),
        )

        y += 16

    if shop_phone:
        _draw_centered_text(
            painter,
            margin,
            y,
            content_width,
            13,
            f"Phone: {shop_phone}",
        )

        y += 14

    y += 3

    _draw_divider(
        painter,
        margin,
        width - margin,
        y,
    )

    y += 7

    # -----------------------------------------------------------------------
    # Receipt title
    # -----------------------------------------------------------------------

    painter.setFont(receipt_title_font)

    _draw_centered_text(
        painter,
        margin,
        y,
        content_width,
        16,
        "CUSTOMER RECEIPT",
    )

    y += 20

    _draw_divider(
        painter,
        margin,
        width - margin,
        y,
    )

    y += 6

    # -----------------------------------------------------------------------
    # Helper for two-column rows
    # -----------------------------------------------------------------------

    def draw_row(
        label: str,
        value: str,
        bold_value: bool = False,
    ) -> None:
        nonlocal y

        label_width = content_width * 0.43
        value_width = content_width * 0.57

        painter.setFont(normal_font)
        painter.setPen(QColor("#000000"))

        _draw_left_text(
            painter,
            margin,
            y,
            label_width,
            14,
            label,
        )

        painter.setFont(
            bold_font if bold_value else value_font
        )

        _draw_right_text(
            painter,
            margin + label_width,
            y,
            value_width,
            14,
            value,
        )

        y += 15

    # -----------------------------------------------------------------------
    # Order details
    # -----------------------------------------------------------------------

    draw_row(
        "Order No:",
        order.order_number,
    )

    draw_row(
        "Date:",
        format_date_display(order.order_date),
    )

    customer_name = (
        order.customer.name
        if order.customer
        else "—"
    )

    draw_row(
        "Customer:",
        customer_name,
    )

    if order.customer and order.customer.mobile:
        draw_row(
            "Mobile:",
            order.customer.mobile,
        )

    draw_row(
        "Delivery:",
        format_date_display(order.delivery_date),
    )

    y += 3

    _draw_divider(
        painter,
        margin,
        width - margin,
        y,
    )

    y += 7

    # -----------------------------------------------------------------------
    # Items header
    # -----------------------------------------------------------------------

    painter.setFont(bold_font)

    # Column positions.
    item_x = margin
    qty_x = margin + content_width * 0.62
    amount_x = margin + content_width * 0.74

    item_width = content_width * 0.60
    qty_width = content_width * 0.12
    amount_width = content_width * 0.26

    _draw_left_text(
        painter,
        item_x,
        y,
        item_width,
        14,
        "Item",
    )

    _draw_right_text(
        painter,
        qty_x,
        y,
        qty_width,
        14,
        "Qty",
    )

    _draw_right_text(
        painter,
        amount_x,
        y,
        amount_width,
        14,
        "Amount",
    )

    y += 15

    _draw_divider(
        painter,
        margin,
        width - margin,
        y,
    )

    y += 4

    # -----------------------------------------------------------------------
    # Items
    # -----------------------------------------------------------------------

    painter.setFont(normal_font)

    for item in (order.items or []):
        clothing_type = str(
            item.clothing_type or "Item"
        )

        quantity = str(
            item.quantity or 0
        )

        amount = format_currency(
            item.price * item.quantity,
            currency,
        )

        # Item name
        painter.setFont(normal_font)

        _draw_left_text(
            painter,
            item_x,
            y,
            item_width,
            16,
            clothing_type,
        )

        # Quantity
        _draw_right_text(
            painter,
            qty_x,
            y,
            qty_width,
            16,
            quantity,
        )

        # Amount
        _draw_right_text(
            painter,
            amount_x,
            y,
            amount_width,
            16,
            amount,
        )

        y += 17

    if not order.items:
        _draw_left_text(
            painter,
            margin,
            y,
            content_width,
            16,
            "No items",
        )

        y += 17

    y += 2

    _draw_divider(
        painter,
        margin,
        width - margin,
        y,
    )

    y += 7

    # -----------------------------------------------------------------------
    # Payment summary
    # -----------------------------------------------------------------------

    draw_row(
        "TOTAL:",
        format_currency(
            order.total_amount,
            currency,
        ),
        bold_value=True,
    )

    draw_row(
        "Paid:",
        format_currency(
            order.paid_amount,
            currency,
        ),
    )

    draw_row(
        "DUE:",
        format_currency(
            order.remaining_amount,
            currency,
        ),
        bold_value=True,
    )

    y += 3

    _draw_divider(
        painter,
        margin,
        width - margin,
        y,
    )

    y += 7

    # -----------------------------------------------------------------------
    # Payment history
    # -----------------------------------------------------------------------

    if payments:
        painter.setFont(bold_font)

        _draw_left_text(
            painter,
            margin,
            y,
            content_width,
            15,
            "PAYMENT HISTORY",
        )

        y += 17

        for payment in payments:
            payment_date = format_date_display(
                payment.payment_date
            )

            method = str(
                payment.payment_method or ""
            )

            payment_text = (
                f"{payment_date} - {method}"
            )

            payment_amount = format_currency(
                payment.amount,
                currency,
            )

            painter.setFont(normal_font)

            _draw_left_text(
                painter,
                margin,
                y,
                content_width * 0.67,
                15,
                payment_text,
            )

            _draw_right_text(
                painter,
                margin + content_width * 0.67,
                y,
                content_width * 0.33,
                15,
                payment_amount,
            )

            y += 16

        y += 3

        _draw_divider(
            painter,
            margin,
            width - margin,
            y,
        )

        y += 7

    # -----------------------------------------------------------------------
    # Special instructions
    # -----------------------------------------------------------------------

    if order.special_instructions:
        painter.setFont(bold_font)

        _draw_left_text(
            painter,
            margin,
            y,
            content_width,
            15,
            "SPECIAL INSTRUCTIONS",
        )

        y += 17

        painter.setFont(normal_font)

        instruction_rect = QRectF(
            margin,
            y,
            content_width,
            70,
        )

        consumed = _draw_wrapped_text(
            painter,
            order.special_instructions,
            instruction_rect,
        )

        y += max(
            18.0,
            consumed,
        )

        y += 3

        _draw_divider(
            painter,
            margin,
            width - margin,
            y,
        )

        y += 7

    # -----------------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------------

    painter.setFont(bold_font)

    _draw_centered_text(
        painter,
        margin,
        y,
        content_width,
        16,
        "Thank you for your business!",
    )

    y += 18

    painter.setFont(small_font)

    _draw_centered_text(
        painter,
        margin,
        y,
        content_width,
        14,
        f"Generated by {shop_name}",
    )

    y += 14

    _draw_centered_text(
        painter,
        margin,
        y,
        content_width,
        14,
        "Tailor Shop Manager",
    )

    y += 18

    # Extra blank space at the end of the receipt.
    y += 10


# ---------------------------------------------------------------------------
# Public thermal printing function
# ---------------------------------------------------------------------------

def print_customer_receipt(
    order_id: int,
    parent_widget: QWidget = None,
):
    """Generate and print a customer receipt for a 58mm POS printer."""

    order_service = OrderService()
    payment_service = PaymentService()

    # -----------------------------------------------------------------------
    # Get order
    # -----------------------------------------------------------------------

    order = order_service.get_order(order_id)

    if not order:
        logger.error(
            f"Order {order_id} not found for receipt printing"
        )
        return

    # -----------------------------------------------------------------------
    # Get shop settings
    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------
    # Get payments
    # -----------------------------------------------------------------------

    payments = payment_service.get_payments_for_order(
        order_id
    )

    # -----------------------------------------------------------------------
    # Create thermal printer
    # -----------------------------------------------------------------------

    printer = QPrinter(
        QPrinter.PrinterMode.HighResolution
    )

    _configure_thermal_printer(printer)

    # -----------------------------------------------------------------------
    # Prefer POS58 Printer if it exists.
    #
    # We set it before showing the dialog so Windows opens the dialog with
    # the POS58 printer already selected.
    # -----------------------------------------------------------------------

    printer.setPrinterName(THERMAL_PRINTER_NAME)

    logger.info(
        f"Preparing receipt for printer: "
        f"{THERMAL_PRINTER_NAME}"
    )

    # -----------------------------------------------------------------------
    # Windows printer dialog
    # -----------------------------------------------------------------------

    dialog = QPrintDialog(
        printer,
        parent_widget,
    )

    dialog.setWindowTitle(
        "Print Receipt - POS58"
    )

    if dialog.exec() != QPrintDialog.DialogCode.Accepted:
        logger.info(
            f"Receipt printing cancelled for order {order.order_number}"
        )
        return

    # -----------------------------------------------------------------------
    # Re-apply thermal settings after dialog.
    #
    # Some Windows printer dialogs/drivers can modify page settings.
    # -----------------------------------------------------------------------

    _configure_thermal_printer(printer)

    # Keep the printer selected by the user.
    #
    # Do NOT call setPrinterName() here again because the user may have
    # selected another printer from the dialog.
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Start painter
    # -----------------------------------------------------------------------

    painter = QPainter()

    if not painter.begin(printer):
        logger.error(
            "Failed to start printing. "
            f"Printer: {printer.printerName()}"
        )
        return

    try:
        _draw_thermal_receipt(
            painter=painter,
            printer=printer,
            order=order,
            payments=payments,
            shop_name=shop_name,
            shop_phone=shop_phone,
            shop_address=shop_address,
            currency=currency,
        )

    except Exception:
        logger.exception(
            f"Error while drawing receipt for "
            f"order {order.order_number}"
        )

        raise

    finally:
        painter.end()

    logger.info(
        f"Receipt sent to printer for order "
        f"{order.order_number}"
    )


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def generate_receipt_pdf(
    order_id: int,
    output_path: str,
) -> bool:
    """Generate a customer receipt as an A4 PDF file silently.

    This function intentionally remains A4 because it is used for PDF
    generation/export and is separate from the physical POS58 receipt.
    """

    order_service = OrderService()
    payment_service = PaymentService()

    order = order_service.get_order(order_id)

    if not order:
        logger.error(
            f"Order {order_id} not found for PDF generation"
        )
        return False

    # -----------------------------------------------------------------------
    # Get shop settings
    # -----------------------------------------------------------------------

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

    payments = payment_service.get_payments_for_order(
        order_id
    )

    # -----------------------------------------------------------------------
    # A4 PDF printer
    # -----------------------------------------------------------------------

    printer = QPrinter(
        QPrinter.PrinterMode.ScreenResolution
    )

    printer.setPageSize(
        QPageSize(
            QPageSize.PageSizeId.A4
        )
    )

    printer.setOutputFormat(
        QPrinter.OutputFormat.PdfFormat
    )

    printer.setOutputFileName(
        output_path
    )

    painter = QPainter()

    if not painter.begin(printer):
        logger.error(
            "Failed to start printing to PDF"
        )
        return False

    try:
        page_rect = printer.pageRect(
            QPrinter.Unit.Point
        )

        width = page_rect.width()

        margin = 40

        content_width = width - 2 * margin

        y = margin

        # ---------------------------------------------------------------
        # Fonts
        # ---------------------------------------------------------------

        title_font = QFont(
            "Public Sans",
            18,
            QFont.Weight.Bold,
        )

        normal_font = QFont(
            "Public Sans",
            10,
        )

        small_font = QFont(
            "Public Sans",
            8,
        )

        header_font = QFont(
            "Public Sans",
            12,
            QFont.Weight.Bold,
        )

        value_font = QFont(
            "Public Sans",
            11,
        )

        # ---------------------------------------------------------------
        # Header
        # ---------------------------------------------------------------

        painter.setFont(title_font)
        painter.setPen(QColor("#091426"))

        painter.drawText(
            QRectF(
                margin,
                y,
                content_width,
                30,
            ),
            Qt.AlignmentFlag.AlignCenter,
            shop_name,
        )

        y += 30

        # Shop details
        painter.setFont(small_font)
        painter.setPen(QColor("#666666"))

        if shop_address:
            painter.drawText(
                QRectF(
                    margin,
                    y,
                    content_width,
                    16,
                ),
                Qt.AlignmentFlag.AlignCenter,
                shop_address,
            )

            y += 16

        if shop_phone:
            painter.drawText(
                QRectF(
                    margin,
                    y,
                    content_width,
                    16,
                ),
                Qt.AlignmentFlag.AlignCenter,
                f"Phone: {shop_phone}",
            )

            y += 16

        y += 10

        # Divider
        painter.setPen(
            QPen(
                QColor("#cccccc"),
                1,
            )
        )

        painter.drawLine(
            QPointF(margin, y),
            QPointF(width - margin, y),
        )

        y += 15

        # ---------------------------------------------------------------
        # Receipt title
        # ---------------------------------------------------------------

        painter.setFont(header_font)
        painter.setPen(QColor("#091426"))

        painter.drawText(
            QRectF(
                margin,
                y,
                content_width,
                20,
            ),
            Qt.AlignmentFlag.AlignCenter,
            "CUSTOMER RECEIPT",
        )

        y += 30

        # ---------------------------------------------------------------
        # Row helper
        # ---------------------------------------------------------------

        def draw_row(
            label: str,
            value: str,
            bold_value: bool = False,
        ):
            nonlocal y

            painter.setFont(normal_font)
            painter.setPen(QColor("#666666"))

            painter.drawText(
                QRectF(
                    margin,
                    y,
                    content_width * 0.4,
                    18,
                ),
                Qt.AlignmentFlag.AlignLeft,
                label,
            )

            painter.setFont(
                value_font
                if bold_value
                else normal_font
            )

            painter.setPen(QColor("#091426"))

            painter.drawText(
                QRectF(
                    margin + content_width * 0.4,
                    y,
                    content_width * 0.6,
                    18,
                ),
                Qt.AlignmentFlag.AlignLeft,
                value,
            )

            y += 20

        # ---------------------------------------------------------------
        # Order details
        # ---------------------------------------------------------------

        draw_row(
            "Order Number:",
            order.order_number,
        )

        draw_row(
            "Date:",
            format_date_display(
                order.order_date
            ),
        )

        draw_row(
            "Customer:",
            (
                order.customer.name
                if order.customer
                else "—"
            ),
        )

        if order.customer and order.customer.mobile:
            draw_row(
                "Mobile:",
                order.customer.mobile,
            )

        draw_row(
            "Delivery Date:",
            format_date_display(
                order.delivery_date
            ),
        )

        y += 10

        painter.setPen(
            QPen(
                QColor("#cccccc"),
                1,
            )
        )

        painter.drawLine(
            QPointF(margin, y),
            QPointF(width - margin, y),
        )

        y += 15

        # ---------------------------------------------------------------
        # Items
        # ---------------------------------------------------------------

        painter.setFont(header_font)
        painter.setPen(QColor("#091426"))

        painter.drawText(
            QRectF(
                margin,
                y,
                content_width,
                20,
            ),
            Qt.AlignmentFlag.AlignLeft,
            "Items",
        )

        y += 25

        for item in (order.items or []):
            draw_row(
                f"  {item.clothing_type} × "
                f"{item.quantity}",
                format_currency(
                    item.price * item.quantity,
                    currency,
                ),
            )

        y += 10

        painter.setPen(
            QPen(
                QColor("#cccccc"),
                1,
            )
        )

        painter.drawLine(
            QPointF(margin, y),
            QPointF(width - margin, y),
        )

        y += 15

        # ---------------------------------------------------------------
        # Payment summary
        # ---------------------------------------------------------------

        draw_row(
            "Total Amount:",
            format_currency(
                order.total_amount,
                currency,
            ),
            bold_value=True,
        )

        draw_row(
            "Paid:",
            format_currency(
                order.paid_amount,
                currency,
            ),
        )

        draw_row(
            "Remaining:",
            format_currency(
                order.remaining_amount,
                currency,
            ),
            bold_value=True,
        )

        y += 10

        painter.setPen(
            QPen(
                QColor("#cccccc"),
                1,
            )
        )

        painter.drawLine(
            QPointF(margin, y),
            QPointF(width - margin, y),
        )

        y += 15

        # ---------------------------------------------------------------
        # Payment history
        # ---------------------------------------------------------------

        if payments:
            painter.setFont(header_font)
            painter.setPen(QColor("#091426"))

            painter.drawText(
                QRectF(
                    margin,
                    y,
                    content_width,
                    20,
                ),
                Qt.AlignmentFlag.AlignLeft,
                "Payment History",
            )

            y += 25

            for payment in payments:
                draw_row(
                    f"  "
                    f"{format_date_display(payment.payment_date)} "
                    f"({payment.payment_method})",
                    format_currency(
                        payment.amount,
                        currency,
                    ),
                )

        y += 20

        # ---------------------------------------------------------------
        # Special instructions
        # ---------------------------------------------------------------

        if order.special_instructions:
            painter.setFont(header_font)
            painter.setPen(QColor("#091426"))

            painter.drawText(
                QRectF(
                    margin,
                    y,
                    content_width,
                    20,
                ),
                Qt.AlignmentFlag.AlignLeft,
                "Special Instructions",
            )

            y += 22

            painter.setFont(normal_font)
            painter.setPen(QColor("#666666"))

            painter.drawText(
                QRectF(
                    margin,
                    y,
                    content_width,
                    60,
                ),
                Qt.AlignmentFlag.AlignLeft
                | Qt.AlignmentFlag.TextWordWrap,
                order.special_instructions,
            )

            y += 50

        # ---------------------------------------------------------------
        # Footer
        # ---------------------------------------------------------------

        y += 20

        painter.setPen(
            QPen(
                QColor("#cccccc"),
                1,
            )
        )

        painter.drawLine(
            QPointF(margin, y),
            QPointF(width - margin, y),
        )

        y += 15

        painter.setFont(small_font)
        painter.setPen(QColor("#999999"))

        painter.drawText(
            QRectF(
                margin,
                y,
                content_width,
                14,
            ),
            Qt.AlignmentFlag.AlignCenter,
            "Thank you for your business!",
        )

        y += 14

        painter.drawText(
            QRectF(
                margin,
                y,
                content_width,
                14,
            ),
            Qt.AlignmentFlag.AlignCenter,
            f"Generated by {shop_name} — "
            f"Tailor Shop Manager",
        )

    except Exception:
        logger.exception(
            f"Error generating receipt PDF "
            f"for order {order.order_number}"
        )

        return False

    finally:
        painter.end()

    logger.info(
        f"Receipt PDF generated for order "
        f"{order.order_number} at {output_path}"
    )

    return True