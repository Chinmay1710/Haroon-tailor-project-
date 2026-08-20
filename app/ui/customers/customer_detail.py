from __future__ import annotations
"""Customer detail page — full customer view with measurements, orders, and payment summary."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QHeaderView, QAbstractItemView, QScrollArea, QFrame)
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG, STACK_MD, CARD_RADIUS
from app.ui.widgets.status_badge import StatusBadge
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService
from app.services.measurement_service import MeasurementService
from app.utils.formatters import format_currency, format_date_display, get_initials


class CustomerDetailPage(QWidget):
    """Customer detail view with info, measurements, order history."""

    go_back = Signal()
    edit_customer_requested = Signal(int)
    delete_customer_requested = Signal(int)
    new_order_for_customer = Signal(int)
    view_order_requested = Signal(int)
    add_measurement_requested = Signal(int)  # customer_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.customer_service = CustomerService()
        self.order_service = OrderService()
        self.measurement_service = MeasurementService()
        self.current_customer_id = None
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

        # Back button
        back_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Customers")
        back_btn.setProperty("cssClass", "text")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.go_back.emit)
        back_row.addWidget(back_btn)
        back_row.addStretch()
        self.main_layout.addLayout(back_row)

        # Customer Info Card
        self.info_card = QWidget()
        self.info_card.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface_container_lowest']};
                border: 1px solid {COLORS['surface_container_low']};
                border-radius: {CARD_RADIUS}px;
            }}
        """)
        info_layout = QHBoxLayout(self.info_card)
        info_layout.setContentsMargins(24, 24, 24, 24)
        info_layout.setSpacing(20)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(64, 64)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.avatar_label)

        info_text = QVBoxLayout()
        info_text.setSpacing(4)
        self.name_label = QLabel()
        self.name_label.setStyleSheet(f"font-size: 24px; font-weight: 600; border: none; background: transparent;")
        info_text.addWidget(self.name_label)
        self.detail_label = QLabel()
        self.detail_label.setStyleSheet(f"font-size: 14px; color: {COLORS['on_surface_variant']}; border: none; background: transparent;")
        info_text.addWidget(self.detail_label)
        info_layout.addLayout(info_text, 1)

        btn_col = QVBoxLayout()
        btn_col.setSpacing(8)
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.clicked.connect(lambda: self.edit_customer_requested.emit(self.current_customer_id))
        btn_col.addWidget(self.edit_btn)

        self.order_btn = QPushButton("🛍️ New Order")
        self.order_btn.setProperty("cssClass", "primary")
        self.order_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.order_btn.clicked.connect(lambda: self.new_order_for_customer.emit(self.current_customer_id))
        btn_col.addWidget(self.order_btn)

        info_layout.addLayout(btn_col)
        self.main_layout.addWidget(self.info_card)

        # Payment Summary
        self.payment_summary = QLabel()
        self.payment_summary.setStyleSheet(f"""
            background-color: {COLORS['surface_container_lowest']};
            border: 1px solid {COLORS['surface_container_low']};
            border-radius: {CARD_RADIUS}px;
            padding: 20px;
            font-size: {FONT_SIZES['body_md']}px;
        """)
        self.main_layout.addWidget(self.payment_summary)

        # Measurements section
        meas_header = QHBoxLayout()
        meas_title = QLabel("📏 Saved Measurements")
        meas_title.setStyleSheet(f"font-size: 20px; font-weight: 600;")
        meas_header.addWidget(meas_title)
        meas_header.addStretch()
        add_meas_btn = QPushButton("+ Add Measurement")
        add_meas_btn.setProperty("cssClass", "primary")
        add_meas_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_meas_btn.clicked.connect(lambda: self.add_measurement_requested.emit(self.current_customer_id))
        meas_header.addWidget(add_meas_btn)
        self.main_layout.addLayout(meas_header)

        self.measurements_container = QVBoxLayout()
        self.measurements_container.setSpacing(8)
        self.main_layout.addLayout(self.measurements_container)

        # Orders section
        orders_title = QLabel("🛍️ Order History")
        orders_title.setStyleSheet(f"font-size: 20px; font-weight: 600;")
        self.main_layout.addWidget(orders_title)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels(
            ["Order #", "Item", "Date", "Total", "Paid", "Remaining", "Status"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.orders_table.setShowGrid(False)
        self.orders_table.setMinimumHeight(200)
        self.orders_table.doubleClicked.connect(self._on_order_double_click)
        self.main_layout.addWidget(self.orders_table)

        # Delete button (bottom, de-emphasized)
        del_row = QHBoxLayout()
        del_row.addStretch()
        del_btn = QPushButton("🗑️ Delete Customer")
        del_btn.setProperty("cssClass", "danger")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(lambda: self.delete_customer_requested.emit(self.current_customer_id))
        del_row.addWidget(del_btn)
        self.main_layout.addLayout(del_row)

        self.main_layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def load_customer(self, customer_id: int):
        self.current_customer_id = customer_id
        try:
            customer = self.customer_service.get_customer(customer_id)
            if not customer:
                return

            # Avatar
            initials = get_initials(customer.name)
            self.avatar_label.setText(initials)
            self.avatar_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['surface_container']};
                    border-radius: 32px;
                    font-size: 24px;
                    font-weight: 600;
                    color: {COLORS['on_surface_variant']};
                    border: none;
                }}
            """)

            self.name_label.setText(customer.name)
            details = []
            if customer.mobile:
                details.append(f"📱 {customer.mobile}")
            if customer.address:
                details.append(f"📍 {customer.address}")
            self.detail_label.setText("  •  ".join(details) if details else "No contact details")

            # Payment summary
            from app.database.engine import get_session
            from app.repositories.settings_repo import SettingsRepository
            session = get_session()
            try:
                settings = SettingsRepository(session).get_settings()
                currency = settings.currency or "₹"
            finally:
                session.close()

            from app.database.engine import get_session
            from app.repositories.order_repo import OrderRepository
            session2 = get_session()
            try:
                orders = OrderRepository(session2).get_by_customer(customer_id)
            finally:
                session2.close()

            total_orders = len(orders)
            total_spent = sum(o.total_amount for o in orders if o.status != "CANCELLED")
            total_paid = sum(o.paid_amount for o in orders if o.status != "CANCELLED")
            total_pending = total_spent - total_paid

            self.payment_summary.setText(
                f"Total Orders: {total_orders}   |   "
                f"Total Spent: {format_currency(total_spent, currency)}   |   "
                f"Total Paid: {format_currency(total_paid, currency)}   |   "
                f"Pending: {format_currency(total_pending, currency)}"
            )

            # Measurements
            while self.measurements_container.count():
                child = self.measurements_container.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            profiles = self.measurement_service.get_profiles_for_customer(customer_id)
            if profiles:
                for profile in profiles:
                    card = QWidget()
                    card.setStyleSheet(f"""
                        QWidget {{
                            background-color: {COLORS['surface_container_lowest']};
                            border: 1px solid {COLORS['surface_container_low']};
                            border-radius: {CARD_RADIUS}px;
                        }}
                    """)
                    card_layout = QVBoxLayout(card)
                    card_layout.setContentsMargins(16, 12, 16, 12)
                    card_layout.setSpacing(4)

                    header_row = QHBoxLayout()
                    pname = QLabel(f"{profile.name} ({profile.template_type})")
                    pname.setStyleSheet(f"font-size: 15px; font-weight: 600; border: none; background: transparent;")
                    header_row.addWidget(pname)
                    header_row.addStretch()
                    unit_lbl = QLabel(f"Unit: {profile.unit}")
                    unit_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS['on_surface_variant']}; border: none; background: transparent;")
                    header_row.addWidget(unit_lbl)
                    card_layout.addLayout(header_row)

                    values_text = "  |  ".join(
                        f"{v.field_name}: {v.field_value}" for v in profile.values if v.field_value
                    )
                    val_label = QLabel(values_text or "No measurements recorded")
                    val_label.setWordWrap(True)
                    val_label.setStyleSheet(f"font-size: 13px; color: {COLORS['on_surface_variant']}; border: none; background: transparent;")
                    card_layout.addWidget(val_label)
                    self.measurements_container.addWidget(card)
            else:
                empty = QLabel("No measurements saved yet")
                empty.setStyleSheet(f"color: {COLORS['on_surface_variant']}; padding: 16px;")
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.measurements_container.addWidget(empty)

            # Orders table
            self.orders_table.setRowCount(len(orders))
            for row, order in enumerate(orders):
                self.orders_table.setItem(row, 0, QTableWidgetItem(order.order_number))
                items_text = ", ".join(i.clothing_type for i in order.items) if order.items else "—"
                self.orders_table.setItem(row, 1, QTableWidgetItem(items_text))
                self.orders_table.setItem(row, 2, QTableWidgetItem(
                    format_date_display(order.order_date)))
                self.orders_table.setItem(row, 3, QTableWidgetItem(
                    format_currency(order.total_amount, currency)))
                self.orders_table.setItem(row, 4, QTableWidgetItem(
                    format_currency(order.paid_amount, currency)))
                remaining = format_currency(order.remaining_amount, currency)
                rem_item = QTableWidgetItem(remaining)
                if order.remaining_amount > 0:
                    from PySide6.QtGui import QColor
                    rem_item.setForeground(QColor(COLORS['error']))
                self.orders_table.setItem(row, 5, rem_item)

                sw = QWidget()
                sl = QHBoxLayout(sw)
                sl.setContentsMargins(4, 4, 4, 4)
                badge = StatusBadge(order.status)
                sl.addWidget(badge)
                sl.addStretch()
                self.orders_table.setCellWidget(row, 6, sw)

            if not orders:
                self.orders_table.setRowCount(1)
                empty_item = QTableWidgetItem("No orders yet")
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.orders_table.setItem(0, 0, empty_item)
                self.orders_table.setSpan(0, 0, 1, 7)

        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Error loading customer detail: {e}")

    def _on_order_double_click(self, index):
        row = index.row()
        item = self.orders_table.item(row, 0)
        if item and item.text().startswith("ORD"):
            from app.database.engine import get_session
            from app.repositories.order_repo import OrderRepository
            session = get_session()
            try:
                order = OrderRepository(session).get_by_order_number(item.text())
                if order:
                    self.view_order_requested.emit(order.id)
            finally:
                session.close()
