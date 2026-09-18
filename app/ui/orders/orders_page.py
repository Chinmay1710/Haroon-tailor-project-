from __future__ import annotations
"""Orders page — list, filter, and manage orders."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QLineEdit, QTableWidget,
                                QTableWidgetItem, QHeaderView, QAbstractItemView,
                                QScrollArea, QComboBox)
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG
from app.ui.widgets.status_badge import StatusBadge
from app.services.order_service import OrderService
from app.utils.formatters import format_currency, format_date_display


class OrdersPage(QWidget):
    """Orders list page with status filters."""

    new_order_requested = Signal()
    view_order_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_service = OrderService()
        self.current_page = 1
        self.page_size = 50
        self.total_count = 0
        self._current_filter = "All"
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(CONTAINER_PADDING, CONTAINER_PADDING,
                                   CONTAINER_PADDING, CONTAINER_PADDING)
        layout.setSpacing(STACK_LG)

        # Header
        header = QHBoxLayout()
        title = QLabel("Orders")
        title.setStyleSheet(f"font-size: 32px; font-weight: 600; color: {COLORS['on_surface']};")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("  ＋  New Order")
        add_btn.setProperty("cssClass", "primary")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self.new_order_requested.emit)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Filters
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        self.filter_buttons = {}
        for status in ["All", "New", "Stitching", "Ready", "Delivered", "Cancelled", "Overdue"]:
            btn = QPushButton(status)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(36)
            btn.clicked.connect(lambda checked, s=status: self._apply_filter(s))
            self.filter_buttons[status] = btn
            filter_row.addWidget(btn)
        self.filter_buttons["All"].setChecked(True)
        self._style_filter_buttons()
        filter_row.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search orders...")
        self.search_input.setFixedWidth(250)
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self._on_search)
        filter_row.addWidget(self.search_input)
        layout.addLayout(filter_row)

        # Count
        self.count_label = QLabel("0 orders")
        self.count_label.setStyleSheet(f"font-size: {FONT_SIZES['label_sm']}px; color: {COLORS['on_surface_variant']};")
        layout.addWidget(self.count_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Order #", "Customer", "Item", "Qty", "Order Date",
            "Delivery", "Total", "Remaining", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(400)
        self.table.doubleClicked.connect(self._on_row_double_click)
        layout.addWidget(self.table)

        self.empty_label = QLabel("No orders found\nCreate your first order!")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"font-size: {FONT_SIZES['body_lg']}px; color: {COLORS['on_surface_variant']}; padding: 60px;")
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)

        # Pagination Controls
        pagination_row = QHBoxLayout()
        pagination_row.addStretch()
        
        self.btn_prev = QPushButton("◄ Previous")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.clicked.connect(self._prev_page)
        
        self.lbl_page = QLabel("Page 1")
        self.lbl_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_page.setFixedWidth(100)
        
        self.btn_next = QPushButton("Next ►")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.clicked.connect(self._next_page)
        
        pagination_row.addWidget(self.btn_prev)
        pagination_row.addWidget(self.lbl_page)
        pagination_row.addWidget(self.btn_next)
        pagination_row.addStretch()
        
        layout.addLayout(pagination_row)

        layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _style_filter_buttons(self):
        for name, btn in self.filter_buttons.items():
            if btn.isChecked():
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['primary']};
                        color: {COLORS['on_primary']};
                        border: none;
                        border-radius: 18px;
                        padding: 0 16px;
                        font-size: {FONT_SIZES['label_sm']}px;
                        font-weight: 600;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['surface_container_lowest']};
                        color: {COLORS['on_surface_variant']};
                        border: 1px solid {COLORS['outline_variant']};
                        border-radius: 18px;
                        padding: 0 16px;
                        font-size: {FONT_SIZES['label_sm']}px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['surface_container_low']};
                    }}
                """)

    def _apply_filter(self, status: str):
        self._current_filter = status
        self.current_page = 1
        for name, btn in self.filter_buttons.items():
            btn.setChecked(name == status)
        self._style_filter_buttons()
        self.refresh_data()

    def _on_search(self, text: str):
        self.current_page = 1
        self.refresh_data()

    def refresh_data(self):
        try:
            from app.database.engine import get_session
            from app.repositories.settings_repo import SettingsRepository
            session = get_session()
            try:
                currency = SettingsRepository(session).get_settings().currency or "₹"
            finally:
                session.close()

            status_filter = None if self._current_filter == "All" else self._current_filter.upper()
            search_text = self.search_input.text().strip()
            offset = (self.current_page - 1) * self.page_size

            if search_text:
                orders, total = self.order_service.search_orders(search_text, limit=self.page_size, offset=offset)
            elif self._current_filter == "Overdue":
                orders, total = self.order_service.get_overdue_orders(limit=self.page_size, offset=offset)
            else:
                orders, total = self.order_service.get_all_orders(status_filter, limit=self.page_size, offset=offset)

            self.total_count = total
            self._update_pagination_ui()
            self._populate_table(orders, currency)
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Error loading orders: {e}")

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_data()
            
    def _next_page(self):
        max_page = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        if self.current_page < max_page:
            self.current_page += 1
            self.refresh_data()
            
    def _update_pagination_ui(self):
        max_page = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        self.lbl_page.setText(f"Page {self.current_page} of {max_page}")
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < max_page)
        self.count_label.setText(f"{self.total_count} order{'s' if self.total_count != 1 else ''}")

    def _populate_table(self, orders: list, currency: str):
        self.table.setRowCount(len(orders))
        self.empty_label.setVisible(len(orders) == 0)
        self.table.setVisible(len(orders) > 0)

        for row, o in enumerate(orders):
            self.table.setItem(row, 0, QTableWidgetItem(o.order_number))
            self.table.setItem(row, 1, QTableWidgetItem(
                o.customer.name if o.customer else "—"))
            items = ", ".join(f"{i.clothing_type}" for i in o.items) if o.items else "—"
            self.table.setItem(row, 2, QTableWidgetItem(items))
            qty = sum(i.quantity for i in o.items) if o.items else 0
            self.table.setItem(row, 3, QTableWidgetItem(str(qty)))
            self.table.setItem(row, 4, QTableWidgetItem(format_date_display(o.order_date)))
            self.table.setItem(row, 5, QTableWidgetItem(format_date_display(o.delivery_date)))
            self.table.setItem(row, 6, QTableWidgetItem(format_currency(o.total_amount, currency)))

            remaining = format_currency(o.remaining_amount, currency)
            rem_item = QTableWidgetItem(remaining)
            if o.remaining_amount > 0:
                from PySide6.QtGui import QColor
                rem_item.setForeground(QColor(COLORS['error']))
            self.table.setItem(row, 7, rem_item)

            status_text = "OVERDUE" if o.is_overdue else o.status
            sw = QWidget()
            sl = QHBoxLayout(sw)
            sl.setContentsMargins(4, 4, 4, 4)
            badge = StatusBadge(status_text)
            sl.addWidget(badge)
            sl.addStretch()
            self.table.setCellWidget(row, 8, sw)

        self.table.resizeRowsToContents()

    def _on_row_double_click(self, index):
        row = index.row()
        id_item = self.table.item(row, 0)
        if id_item:
            order_num = id_item.text()
            order = self.order_service.get_order_by_number(order_num)
            if order:
                self.view_order_requested.emit(order.id)
