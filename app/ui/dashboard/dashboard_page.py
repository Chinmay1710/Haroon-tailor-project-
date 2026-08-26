from __future__ import annotations
"""Dashboard page — main overview with summary cards, pipeline, deliveries, and quick actions."""

from datetime import date, datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QScrollArea, QGridLayout, QFrame, QTableWidget,
                                QTableWidgetItem, QHeaderView, QPushButton, QSizePolicy,
                                QAbstractItemView)
from PySide6.QtCore import Signal, Qt

from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG, STACK_MD, STACK_SM
from app.ui.widgets.cards import SummaryCard, QuickActionCard, StatusCountCard
from app.ui.widgets.status_badge import StatusBadge
from app.services.order_service import OrderService
from app.utils.formatters import format_currency, get_greeting, get_initials, format_date_display


class DashboardPage(QWidget):
    """Dashboard page matching the Stitch design."""

    navigate_to = Signal(str)         # navigate to a page
    new_order_requested = Signal()
    add_customer_requested = Signal()
    add_payment_requested = Signal()
    add_expense_requested = Signal()
    view_order_requested = Signal(int)  # order id
    backup_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_service = OrderService()
        self._setup_ui()

    def _setup_ui(self):
        # Scroll area wrapper
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

        # ─── Welcome Header ───
        self.greeting_label = QLabel()
        self.greeting_label.setStyleSheet(f"""
            font-size: 40px; font-weight: 700;
            color: {COLORS['on_surface']};
            letter-spacing: -0.02em;
        """)
        self.main_layout.addWidget(self.greeting_label)

        self.date_subtitle = QLabel()
        self.date_subtitle.setStyleSheet(f"""
            font-size: {FONT_SIZES['body_lg']}px;
            color: {COLORS['on_surface_variant']};
            margin-top: -8px;
        """)
        self.main_layout.addWidget(self.date_subtitle)

        # ─── Summary Cards ───
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(STACK_MD)

        self.orders_today_card = SummaryCard("🛍️", "Orders Today", "0",
                                              COLORS['surface_container_highest'])
        self.sales_today_card = SummaryCard("💰", "Today's Sales", "₹0",
                                             COLORS['tertiary_fixed'])
        self.pending_card = SummaryCard("💳", "Pending Payments", "₹0",
                                         COLORS['error_container'])
        self.deliveries_card = SummaryCard("🚚", "Deliveries Today", "0",
                                            "#bcc7de")

        for card in [self.orders_today_card, self.sales_today_card,
                     self.pending_card, self.deliveries_card]:
            cards_layout.addWidget(card, 1)
        self.main_layout.addLayout(cards_layout)

        # ─── Two Column Layout ───
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(STACK_LG)

        # Left column (wider)
        left_column = QVBoxLayout()
        left_column.setSpacing(STACK_LG)

        # Order Pipeline
        pipeline_header = QHBoxLayout()
        pipeline_title = QLabel("Order Pipeline")
        pipeline_title.setStyleSheet(f"""
            font-size: {FONT_SIZES['headline_md']}px;
            font-weight: 600;
        """)
        pipeline_header.addWidget(pipeline_title)
        pipeline_header.addStretch()
        view_all_btn = QPushButton("View All")
        view_all_btn.setProperty("cssClass", "text")
        view_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_all_btn.clicked.connect(lambda: self.navigate_to.emit("orders"))
        pipeline_header.addWidget(view_all_btn)
        left_column.addLayout(pipeline_header)

        pipeline_grid = QHBoxLayout()
        pipeline_grid.setSpacing(STACK_SM)
        self.pipeline_cards = {
            "NEW": StatusCountCard("0", "New"),
            "CUTTING_COMPLETE": StatusCountCard("0", "Cut Done", "#3b82f6"),
            "STITCHING_COMPLETE": StatusCountCard("0", "Stitch Done", "#10b981"),
            "DELIVERED": StatusCountCard("0", "Delivered"),
            "OVERDUE": StatusCountCard("0", "Overdue", "#ef4444"),
        }
        for card in self.pipeline_cards.values():
            pipeline_grid.addWidget(card, 1)
        left_column.addLayout(pipeline_grid)

        # Today's Deliveries Table
        deliveries_title = QLabel("Today's Deliveries")
        deliveries_title.setStyleSheet(f"""
            font-size: {FONT_SIZES['headline_md']}px;
            font-weight: 600;
        """)
        left_column.addWidget(deliveries_title)

        self.deliveries_table = QTableWidget()
        self.deliveries_table.setColumnCount(6)
        self.deliveries_table.setHorizontalHeaderLabels(
            ["Order No", "Customer", "Item", "Status", "Remaining", "Action"]
        )
        self.deliveries_table.horizontalHeader().setStretchLastSection(True)
        self.deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.deliveries_table.verticalHeader().setVisible(False)
        self.deliveries_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.deliveries_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.deliveries_table.setMinimumHeight(200)
        self.deliveries_table.setShowGrid(False)
        self.deliveries_table.setAlternatingRowColors(False)
        left_column.addWidget(self.deliveries_table)

        columns_layout.addLayout(left_column, 2)

        # Right column
        right_column = QVBoxLayout()
        right_column.setSpacing(STACK_LG)

        # Quick Actions
        qa_title = QLabel("Quick Actions")
        qa_title.setStyleSheet(f"""
            font-size: {FONT_SIZES['headline_md']}px;
            font-weight: 600;
        """)
        right_column.addWidget(qa_title)

        qa_grid = QGridLayout()
        qa_grid.setSpacing(STACK_SM)

        btn_customer = QuickActionCard("👤", "Add Customer")
        btn_customer.clicked.connect(self.add_customer_requested.emit)
        qa_grid.addWidget(btn_customer, 0, 0)

        btn_order = QuickActionCard("➕", "New Order", primary=True)
        btn_order.clicked.connect(self.new_order_requested.emit)
        qa_grid.addWidget(btn_order, 0, 1)

        btn_payment = QuickActionCard("💳", "Add Payment")
        btn_payment.clicked.connect(self.add_payment_requested.emit)
        qa_grid.addWidget(btn_payment, 1, 0)

        btn_expense = QuickActionCard("📋", "Add Expense")
        btn_expense.clicked.connect(self.add_expense_requested.emit)
        qa_grid.addWidget(btn_expense, 1, 1)

        btn_receipt = QuickActionCard("🖨️", "Print Receipt")
        qa_grid.addWidget(btn_receipt, 2, 0)

        btn_backup = QuickActionCard("💾", "Backup Data")
        btn_backup.clicked.connect(self.backup_requested.emit)
        qa_grid.addWidget(btn_backup, 2, 1)

        right_column.addLayout(qa_grid)

        # Recent Orders
        recent_title = QLabel("Recent Orders")
        recent_title.setStyleSheet(f"""
            font-size: {FONT_SIZES['headline_md']}px;
            font-weight: 600;
        """)
        right_column.addWidget(recent_title)

        self.recent_orders_container = QVBoxLayout()
        self.recent_orders_container.setSpacing(8)
        right_column.addLayout(self.recent_orders_container)

        right_column.addStretch()
        columns_layout.addLayout(right_column, 1)

        self.main_layout.addLayout(columns_layout)
        self.main_layout.addStretch()

        scroll.setWidget(content)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def refresh_data(self):
        """Load fresh data from database and update all dashboard widgets."""
        try:
            data = self.order_service.get_dashboard_data()

            # Greeting
            from app.database.engine import get_session
            from app.repositories.settings_repo import SettingsRepository
            session = get_session()
            try:
                settings = SettingsRepository(session).get_settings()
                owner = settings.owner_name or "there"
                currency = settings.currency or "₹"
            finally:
                session.close()

            greeting = get_greeting()
            self.greeting_label.setText(f"{greeting}, {owner}!")
            today = datetime.now()
            self.date_subtitle.setText(
                f"Today is {today.strftime('%A, %B %d, %Y')}. Let's see what needs to be done."
            )

            # Summary cards
            self.orders_today_card.set_value(str(data["orders_today"]))
            self.sales_today_card.set_value(format_currency(data["today_sales"], currency))
            self.pending_card.set_value(format_currency(data["pending_payments"], currency))
            self.deliveries_card.set_value(str(data["deliveries_today"]))

            # Pipeline
            counts = data["status_counts"]
            for key, card in self.pipeline_cards.items():
                card.set_count(str(counts.get(key, 0)))

            # Today's Deliveries Table
            deliveries = data["today_deliveries_list"]
            self.deliveries_table.setRowCount(len(deliveries))
            for row, order in enumerate(deliveries):
                self.deliveries_table.setItem(row, 0, QTableWidgetItem(order.order_number))
                self.deliveries_table.setItem(row, 1, QTableWidgetItem(
                    order.customer.name if order.customer else "—"))
                items_text = ", ".join(
                    f"{item.quantity}x {item.clothing_type}" for item in order.items
                ) if order.items else "—"
                self.deliveries_table.setItem(row, 2, QTableWidgetItem(items_text))

                status_widget = QWidget()
                sl = QHBoxLayout(status_widget)
                sl.setContentsMargins(4, 4, 4, 4)
                badge = StatusBadge(order.status)
                sl.addWidget(badge)
                sl.addStretch()
                self.deliveries_table.setCellWidget(row, 3, status_widget)

                remaining = format_currency(order.remaining_amount, currency)
                remaining_item = QTableWidgetItem(remaining)
                if order.remaining_amount > 0:
                    remaining_item.setForeground(Qt.GlobalColor.red)
                self.deliveries_table.setItem(row, 4, remaining_item)

                view_btn = QPushButton("›")
                view_btn.setFixedSize(32, 32)
                view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                view_btn.setStyleSheet(f"""
                    QPushButton {{
                        border: none;
                        border-radius: 16px;
                        font-size: 18px;
                        font-weight: bold;
                        color: {COLORS['primary']};
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['surface_container_low']};
                    }}
                """)
                order_id = order.id
                view_btn.clicked.connect(lambda checked, oid=order_id: self.view_order_requested.emit(oid))
                action_widget = QWidget()
                al = QHBoxLayout(action_widget)
                al.setContentsMargins(0, 0, 0, 0)
                al.addStretch()
                al.addWidget(view_btn)
                self.deliveries_table.setCellWidget(row, 5, action_widget)

            self.deliveries_table.setRowCount(max(len(deliveries), 0))
            if not deliveries:
                self.deliveries_table.setRowCount(1)
                empty_item = QTableWidgetItem("No deliveries scheduled for today")
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.deliveries_table.setItem(0, 0, empty_item)
                self.deliveries_table.setSpan(0, 0, 1, 6)

            # Recent Orders
            # Clear existing
            while self.recent_orders_container.count():
                child = self.recent_orders_container.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            for order in data["recent_orders"]:
                card = self._create_recent_order_card(order, currency)
                self.recent_orders_container.addWidget(card)

            if not data["recent_orders"]:
                empty = QLabel("No recent orders")
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                empty.setStyleSheet(f"color: {COLORS['on_surface_variant']}; padding: 20px;")
                self.recent_orders_container.addWidget(empty)

        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Dashboard refresh error: {e}")

    def _create_recent_order_card(self, order, currency: str) -> QWidget:
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface_container_lowest']};
                border: 1px solid {COLORS['surface_container_low']};
                border-radius: 12px;
            }}
        """)
        card.setFixedHeight(64)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Avatar
        initials = get_initials(order.customer.name) if order.customer else "?"
        avatar = QLabel(initials)
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['surface_container']};
                border-radius: 20px;
                font-size: {FONT_SIZES['label_sm']}px;
                font-weight: 600;
                color: {COLORS['on_surface_variant']};
                border: none;
            }}
        """)
        layout.addWidget(avatar)

        # Text
        text_widget = QWidget()
        text_widget.setStyleSheet("border: none; background: transparent;")
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        name_label = QLabel(order.customer.name if order.customer else "—")
        name_label.setStyleSheet(f"""
            font-size: {FONT_SIZES['label_lg']}px;
            font-weight: 600;
            border: none;
        """)
        text_layout.addWidget(name_label)

        items_text = ", ".join(item.clothing_type for item in order.items) if order.items else ""
        sub_label = QLabel(f"#{order.order_number} • {items_text}")
        sub_label.setStyleSheet(f"""
            font-size: {FONT_SIZES['label_sm']}px;
            color: {COLORS['on_surface_variant']};
            border: none;
        """)
        text_layout.addWidget(sub_label)
        layout.addWidget(text_widget, 1)

        # Status badge
        badge = StatusBadge(order.status)
        layout.addWidget(badge)

        return card
