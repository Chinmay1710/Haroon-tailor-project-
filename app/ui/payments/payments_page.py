from __future__ import annotations
"""Payments page — list and add payments."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QHeaderView, QAbstractItemView, QScrollArea)
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG
from app.ui.widgets.status_badge import StatusBadge
from app.services.payment_service import PaymentService
from app.utils.formatters import format_currency, format_date_display


class PaymentsPage(QWidget):
    """Payments list page."""
    add_payment_requested = Signal()
    view_order_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.payment_service = PaymentService()
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(CONTAINER_PADDING, CONTAINER_PADDING, CONTAINER_PADDING, CONTAINER_PADDING)
        layout.setSpacing(STACK_LG)

        header = QHBoxLayout()
        title = QLabel("Payments")
        title.setStyleSheet(f"font-size: 32px; font-weight: 600; color: {COLORS['on_surface']};")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("  ＋  Add Payment")
        add_btn.setProperty("cssClass", "primary")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self.add_payment_requested.emit)
        header.addWidget(add_btn)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Order #", "Customer", "Amount", "Method", "Note"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)

        self.empty_label = QLabel("No payments found")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"font-size: {FONT_SIZES['body_lg']}px; color: {COLORS['on_surface_variant']}; padding: 60px;")
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)
        layout.addStretch()
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh_data(self):
        try:
            from app.database.engine import get_session
            from app.repositories.settings_repo import SettingsRepository
            session = get_session()
            try:
                currency = SettingsRepository(session).get_settings().currency or "₹"
            finally:
                session.close()

            payments = self.payment_service.get_all_payments()
            self.table.setRowCount(len(payments))
            self.empty_label.setVisible(len(payments) == 0)
            self.table.setVisible(len(payments) > 0)
            for row, p in enumerate(payments):
                self.table.setItem(row, 0, QTableWidgetItem(format_date_display(p.payment_date)))
                self.table.setItem(row, 1, QTableWidgetItem(p.order.order_number if p.order else "—"))
                self.table.setItem(row, 2, QTableWidgetItem(p.customer.name if p.customer else "—"))
                self.table.setItem(row, 3, QTableWidgetItem(format_currency(p.amount, currency)))
                self.table.setItem(row, 4, QTableWidgetItem(p.payment_method))
                self.table.setItem(row, 5, QTableWidgetItem(p.note or "—"))
            self.table.resizeRowsToContents()
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Error loading payments: {e}")
