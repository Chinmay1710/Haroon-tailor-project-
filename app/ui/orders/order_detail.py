from __future__ import annotations
"""Order detail page — full order view with actions."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QHeaderView, QAbstractItemView, QScrollArea,
                                QComboBox)
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG, CARD_RADIUS
from app.ui.widgets.status_badge import StatusBadge
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.utils.formatters import format_currency, format_date_display


class OrderDetailPage(QWidget):
    """Order detail view with all info and actions."""

    go_back = Signal()
    print_receipt = Signal(int)
    print_slip = Signal(int)
    add_payment_for_order = Signal(int)
    order_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_service = OrderService()
        self.payment_service = PaymentService()
        self.current_order_id = None
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(CONTAINER_PADDING, CONTAINER_PADDING,
                                             CONTAINER_PADDING, CONTAINER_PADDING)
        self.main_layout.setSpacing(STACK_LG)

        # Back
        back_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Orders")
        back_btn.setProperty("cssClass", "text")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.go_back.emit)
        back_row.addWidget(back_btn)
        back_row.addStretch()
        self.main_layout.addLayout(back_row)

        # Order header card
        self.order_header = QWidget()
        self.order_header.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface_container_lowest']};
                border: 1px solid {COLORS['surface_container_low']};
                border-radius: {CARD_RADIUS}px;
            }}
        """)
        header_layout = QHBoxLayout(self.order_header)
        header_layout.setContentsMargins(24, 20, 24, 20)

        self.order_title = QLabel()
        self.order_title.setStyleSheet("font-size: 24px; font-weight: 600; border: none; background: transparent;")
        header_layout.addWidget(self.order_title)
        header_layout.addStretch()

        self.status_badge_widget = QWidget()
        self.status_badge_widget.setStyleSheet("border: none; background: transparent;")
        self.status_badge_layout = QHBoxLayout(self.status_badge_widget)
        self.status_badge_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(self.status_badge_widget)

        self.main_layout.addWidget(self.order_header)

        # Info grid
        self.info_card = QLabel()
        self.info_card.setWordWrap(True)
        self.info_card.setStyleSheet(f"""
            background-color: {COLORS['surface_container_lowest']};
            border: 1px solid {COLORS['surface_container_low']};
            border-radius: {CARD_RADIUS}px;
            padding: 20px;
            font-size: {FONT_SIZES['body_md']}px;
            line-height: 28px;
        """)
        self.main_layout.addWidget(self.info_card)

        # Measurements card
        self.measurements_card = QLabel()
        self.measurements_card.setWordWrap(True)
        self.measurements_card.setStyleSheet(f"""
            background-color: {COLORS['surface_container_lowest']};
            border: 1px solid {COLORS['surface_container_low']};
            border-radius: {CARD_RADIUS}px;
            padding: 20px;
            font-size: {FONT_SIZES['body_md']}px;
        """)
        self.main_layout.addWidget(self.measurements_card)

        # Payment summary
        self.payment_card = QLabel()
        self.payment_card.setWordWrap(True)
        self.payment_card.setStyleSheet(f"""
            background-color: {COLORS['surface_container_lowest']};
            border: 1px solid {COLORS['surface_container_low']};
            border-radius: {CARD_RADIUS}px;
            padding: 20px;
            font-size: {FONT_SIZES['body_md']}px;
        """)
        self.main_layout.addWidget(self.payment_card)

        # Payment history table
        pay_title = QLabel("💳 Payment History")
        pay_title.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.main_layout.addWidget(pay_title)

        self.pay_table = QTableWidget()
        self.pay_table.setColumnCount(4)
        self.pay_table.setHorizontalHeaderLabels(["Date", "Amount", "Method", "Note"])
        self.pay_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pay_table.verticalHeader().setVisible(False)
        self.pay_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.pay_table.setShowGrid(False)
        self.pay_table.setMinimumHeight(120)
        self.main_layout.addWidget(self.pay_table)

        # Actions row
        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.status_combo = QComboBox()
        self.status_combo.setFixedHeight(40)
        self.status_combo.setFixedWidth(160)
        actions.addWidget(QLabel("Change Status:"))
        actions.addWidget(self.status_combo)

        change_btn = QPushButton("Update Status")
        change_btn.setProperty("cssClass", "primary")
        change_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_btn.clicked.connect(self._change_status)
        actions.addWidget(change_btn)

        actions.addStretch()

        pay_btn = QPushButton("💳 Add Payment")
        pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pay_btn.clicked.connect(lambda: self.add_payment_for_order.emit(self.current_order_id))
        actions.addWidget(pay_btn)

        receipt_btn = QPushButton("🖨️ Receipt")
        receipt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        receipt_btn.clicked.connect(lambda: self.print_receipt.emit(self.current_order_id))
        actions.addWidget(receipt_btn)

        slip_btn = QPushButton("📋 Slip")
        slip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        slip_btn.clicked.connect(lambda: self.print_slip.emit(self.current_order_id))
        actions.addWidget(slip_btn)

        self.main_layout.addLayout(actions)

        # Cancel order (de-emphasized)
        cancel_row = QHBoxLayout()
        cancel_row.addStretch()
        cancel_btn = QPushButton("Cancel Order")
        cancel_btn.setProperty("cssClass", "danger")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self._cancel_order)
        cancel_row.addWidget(cancel_btn)
        self.main_layout.addLayout(cancel_row)

        self.main_layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def load_order(self, order_id: int):
        self.current_order_id = order_id
        try:
            order = self.order_service.get_order(order_id)
            if not order:
                return

            from app.database.engine import get_session
            from app.repositories.settings_repo import SettingsRepository
            session = get_session()
            try:
                currency = SettingsRepository(session).get_settings().currency or "₹"
            finally:
                session.close()

            self.order_title.setText(f"Order {order.order_number}")

            # Status badge
            while self.status_badge_layout.count():
                child = self.status_badge_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            status_text = "OVERDUE" if order.is_overdue else order.status
            self.status_badge_layout.addWidget(StatusBadge(status_text))

            # Info
            customer = order.customer
            items_text = "\n".join(
                f"  • {item.clothing_type} × {item.quantity} — {format_currency(item.price, currency)}"
                for item in order.items
            ) if order.items else "  No items"

            self.info_card.setText(
                f"👤 Customer: {customer.name if customer else '—'}\n"
                f"📱 Mobile: {customer.mobile if customer and customer.mobile else '—'}\n\n"
                f"🛍️ Items:\n{items_text}\n\n"
                f"📅 Order Date: {format_date_display(order.order_date)}\n"
                f"📅 Delivery Date: {format_date_display(order.delivery_date)}\n\n"
                f"📝 Instructions: {order.special_instructions or 'None'}"
            )

            # Measurements
            meas_lines = []
            for item in (order.items or []):
                if item.measurements:
                    meas_lines.append(f"📏 {item.clothing_type} Measurements:")
                    for m in item.measurements:
                        meas_lines.append(f"  {m.field_name}: {m.field_value} {m.unit}")
            self.measurements_card.setText(
                "\n".join(meas_lines) if meas_lines else "No measurements recorded"
            )

            # Payment summary
            self.payment_card.setText(
                f"💰 Total: {format_currency(order.total_amount, currency)}\n"
                f"💵 Paid: {format_currency(order.paid_amount, currency)}\n"
                f"💳 Remaining: {format_currency(order.remaining_amount, currency)}\n"
                f"📊 Payment Status: {order.payment_status}"
            )

            # Payment history
            payments = self.payment_service.get_payments_for_order(order_id)
            self.pay_table.setRowCount(len(payments))
            for row, p in enumerate(payments):
                self.pay_table.setItem(row, 0, QTableWidgetItem(format_date_display(p.payment_date)))
                self.pay_table.setItem(row, 1, QTableWidgetItem(format_currency(p.amount, currency)))
                self.pay_table.setItem(row, 2, QTableWidgetItem(p.payment_method))
                self.pay_table.setItem(row, 3, QTableWidgetItem(p.note or "—"))

            # Status combo
            from app.services.order_service import VALID_TRANSITIONS
            self.status_combo.clear()
            transitions = VALID_TRANSITIONS.get(order.status, [])
            self.status_combo.addItems(transitions if transitions else ["No transitions available"])
            self.status_combo.setEnabled(bool(transitions))

        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Error loading order detail: {e}")

    def _change_status(self):
        new_status = self.status_combo.currentText()
        if not new_status or new_status == "No transitions available":
            return
        from app.ui.widgets.dialogs import ConfirmDialog
        dlg = ConfirmDialog("Change Status",
                            f"Change order status to {new_status}?",
                            "Change", parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            try:
                self.order_service.update_status(self.current_order_id, new_status)
                self.load_order(self.current_order_id)
                self.order_updated.emit()
            except Exception as e:
                from app.ui.widgets.dialogs import MessageDialog
                MessageDialog("Error", str(e), "❌", self).exec()

    def _cancel_order(self):
        from app.ui.widgets.dialogs import ConfirmDialog
        dlg = ConfirmDialog("Cancel Order",
                            "Are you sure you want to cancel this order? This cannot be undone.",
                            "Cancel Order", danger=True, parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            try:
                self.order_service.update_status(self.current_order_id, "CANCELLED")
                self.load_order(self.current_order_id)
                self.order_updated.emit()
            except Exception as e:
                from app.ui.widgets.dialogs import MessageDialog
                MessageDialog("Error", str(e), "❌", self).exec()
