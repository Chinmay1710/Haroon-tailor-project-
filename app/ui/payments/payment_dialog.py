from __future__ import annotations
"""Payment dialog — add payment to an order."""

from datetime import date
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QLineEdit, QComboBox, QDateEdit,
                                QFormLayout, QTextEdit)
from PySide6.QtCore import Qt, QDate
from app.ui.theme import COLORS, FONT_SIZES
from app.config import PAYMENT_METHODS
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.utils.formatters import format_currency
from app.utils.validators import validate_amount


class PaymentDialog(QDialog):
    """Dialog for adding a payment to an order."""

    def __init__(self, order_id: int = None, parent=None):
        super().__init__(parent)
        self.order_service = OrderService()
        self.payment_service = PaymentService()
        self.order_id = order_id
        self.result_data = None
        self.setWindowTitle("Add Payment")
        self.setFixedWidth(480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['surface_container_lowest']}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Add Payment")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; color: {COLORS['primary']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        # Order selector
        if not self.order_id:
            self.order_combo = QComboBox()
            self.order_combo.setFixedHeight(40)
            self._load_orders()
            self.order_combo.currentIndexChanged.connect(self._on_order_selected)
            form.addRow("Order:", self.order_combo)
        else:
            order = self.order_service.get_order(self.order_id)
            if order:
                lbl = QLabel(f"{order.order_number} — {order.customer.name if order.customer else ''}")
                lbl.setStyleSheet(f"font-size: {FONT_SIZES['body_md']}px;")
                form.addRow("Order:", lbl)

        self.remaining_label = QLabel("Remaining: ₹0")
        self.remaining_label.setStyleSheet(f"font-size: {FONT_SIZES['body_md']}px; font-weight: 600; color: {COLORS['error']};")
        form.addRow("", self.remaining_label)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Payment amount")
        self.amount_input.setFixedHeight(42)
        form.addRow("Amount:", self.amount_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setFixedHeight(42)
        form.addRow("Date:", self.date_input)

        self.method_combo = QComboBox()
        self.method_combo.addItems(PAYMENT_METHODS)
        self.method_combo.setFixedHeight(42)
        form.addRow("Method:", self.method_combo)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(60)
        self.note_input.setPlaceholderText("Optional note")
        form.addRow("Note:", self.note_input)

        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setProperty("cssClass", "error")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        save_btn = QPushButton("Add Payment")
        save_btn.setProperty("cssClass", "primary")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        if self.order_id:
            self._update_remaining()

    def _load_orders(self):
        try:
            orders = self.order_service.get_all_orders()
            for o in orders:
                if o.status != "CANCELLED" and o.remaining_amount > 0:
                    self.order_combo.addItem(
                        f"{o.order_number} — {o.customer.name if o.customer else ''} (Remaining: {format_currency(o.remaining_amount)})",
                        o.id)
        except Exception:
            pass

    def _on_order_selected(self):
        self._update_remaining()

    def _update_remaining(self):
        oid = self.order_id or (self.order_combo.currentData() if hasattr(self, 'order_combo') else None)
        if oid:
            order = self.order_service.get_order(oid)
            if order:
                self.remaining_label.setText(f"Remaining: {format_currency(order.remaining_amount)}")

    def _on_save(self):
        oid = self.order_id or (self.order_combo.currentData() if hasattr(self, 'order_combo') else None)
        if not oid:
            self.error_label.setText("Please select an order")
            self.error_label.setVisible(True)
            return

        amount, err = validate_amount(self.amount_input.text(), "Amount")
        if err:
            self.error_label.setText(err)
            self.error_label.setVisible(True)
            return

        qdate = self.date_input.date()
        payment_date = date(qdate.year(), qdate.month(), qdate.day())

        try:
            self.payment_service.add_payment(
                order_id=oid,
                amount=amount,
                payment_date=payment_date,
                payment_method=self.method_combo.currentText(),
                note=self.note_input.toPlainText().strip(),
            )
            self.accept()
        except ValueError as e:
            self.error_label.setText(str(e))
            self.error_label.setVisible(True)
        except Exception as e:
            self.error_label.setText("Unable to save payment. Please try again.")
            self.error_label.setVisible(True)
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Payment error: {e}")
