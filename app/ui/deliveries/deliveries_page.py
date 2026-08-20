from __future__ import annotations
"""Deliveries page — delivery tracking grouped by timeline."""

from datetime import date, timedelta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QHeaderView, QAbstractItemView, QScrollArea)
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG, STACK_MD, CARD_RADIUS
from app.ui.widgets.status_badge import StatusBadge
from app.ui.widgets.dialogs import ConfirmDialog
from app.services.order_service import OrderService
from app.utils.formatters import format_currency, format_date_display


class DeliveriesPage(QWidget):
    """Deliveries page with timeline sections."""
    view_order_requested = Signal(int)
    order_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_service = OrderService()
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(CONTAINER_PADDING, CONTAINER_PADDING, CONTAINER_PADDING, CONTAINER_PADDING)
        self.main_layout.setSpacing(STACK_LG)

        title = QLabel("Deliveries")
        title.setStyleSheet(f"font-size: 32px; font-weight: 600; color: {COLORS['on_surface']};")
        self.main_layout.addWidget(title)

        # Sections will be dynamically built
        self.sections_container = QVBoxLayout()
        self.sections_container.setSpacing(STACK_LG)
        self.main_layout.addLayout(self.sections_container)

        self.main_layout.addStretch()
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh_data(self):
        while self.sections_container.count():
            child = self.sections_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

        try:
            from app.database.engine import get_session
            from app.repositories.order_repo import OrderRepository
            from app.repositories.settings_repo import SettingsRepository

            session = get_session()
            try:
                repo = OrderRepository(session)
                currency = SettingsRepository(session).get_settings().currency or "₹"
                today = date.today()
                tomorrow = today + timedelta(days=1)

                overdue = repo.get_overdue()
                due_today = repo.get_by_delivery_date(today)
                due_tomorrow = repo.get_by_delivery_date(tomorrow)
                upcoming = repo.get_upcoming_deliveries(7)

                self._add_section("⚠️ Overdue", overdue, currency, "#ef4444")
                self._add_section("📅 Due Today", due_today, currency, "#3b82f6")
                self._add_section("📅 Due Tomorrow", due_tomorrow, currency, "#f59e0b")
                self._add_section("📅 Upcoming (7 days)", upcoming, currency)

            finally:
                session.close()
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Error loading deliveries: {e}")

    def _add_section(self, title_text: str, orders: list, currency: str, accent: str = None):
        section_title = QLabel(f"{title_text} ({len(orders)})")
        section_title.setStyleSheet(f"""
            font-size: {FONT_SIZES['headline_md']}px;
            font-weight: 600;
            color: {accent or COLORS['on_surface']};
        """)
        self.sections_container.addWidget(section_title)

        if not orders:
            empty = QLabel("No orders in this section")
            empty.setStyleSheet(f"color: {COLORS['on_surface_variant']}; padding: 12px;")
            self.sections_container.addWidget(empty)
            return

        for order in orders:
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background-color: {COLORS['surface_container_lowest']};
                    border: 1px solid {COLORS['surface_container_low']};
                    border-radius: {CARD_RADIUS}px;
                    {"border-left: 4px solid " + accent + ";" if accent else ""}
                }}
            """)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 12, 16, 12)
            card_layout.setSpacing(16)

            info = QVBoxLayout()
            info.setSpacing(2)
            top_row = QLabel(f"{order.order_number} — {order.customer.name if order.customer else '—'}")
            top_row.setStyleSheet(f"font-size: 15px; font-weight: 600; border: none; background: transparent;")
            info.addWidget(top_row)

            items = ", ".join(i.clothing_type for i in order.items) if order.items else "—"
            sub = QLabel(f"{items}  •  Due: {format_date_display(order.delivery_date)}")
            sub.setStyleSheet(f"font-size: 13px; color: {COLORS['on_surface_variant']}; border: none; background: transparent;")
            info.addWidget(sub)
            card_layout.addLayout(info, 1)

            badge = StatusBadge(order.payment_status)
            card_layout.addWidget(badge)
            badge2 = StatusBadge("OVERDUE" if order.is_overdue else order.status)
            card_layout.addWidget(badge2)

            # Actions
            if order.status not in ("DELIVERED", "CANCELLED"):
                if order.status != "READY":
                    ready_btn = QPushButton("✅ Ready")
                    ready_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    ready_btn.setFixedHeight(32)
                    oid = order.id
                    ready_btn.clicked.connect(lambda checked, i=oid: self._mark_ready(i))
                    card_layout.addWidget(ready_btn)

                deliver_btn = QPushButton("🚚 Delivered")
                deliver_btn.setProperty("cssClass", "primary")
                deliver_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                deliver_btn.setFixedHeight(32)
                oid2 = order.id
                deliver_btn.clicked.connect(lambda checked, i=oid2: self._mark_delivered(i))
                card_layout.addWidget(deliver_btn)

            view_btn = QPushButton("View")
            view_btn.setProperty("cssClass", "text")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            oid3 = order.id
            view_btn.clicked.connect(lambda checked, i=oid3: self.view_order_requested.emit(i))
            card_layout.addWidget(view_btn)

            self.sections_container.addWidget(card)

    def _mark_ready(self, order_id: int):
        try:
            self.order_service.update_status(order_id, "READY")
            self.refresh_data()
            self.order_updated.emit()
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Status change error: {e}")

    def _mark_delivered(self, order_id: int):
        dlg = ConfirmDialog("Mark as Delivered",
                            "Are you sure you want to mark this order as delivered?",
                            "Mark Delivered", parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            try:
                order = self.order_service.get_order(order_id)
                if order and order.status != "READY":
                    self.order_service.update_status(order_id, "READY")
                self.order_service.update_status(order_id, "DELIVERED")
                self.refresh_data()
                self.order_updated.emit()
            except Exception as e:
                from app.ui.widgets.dialogs import MessageDialog
                MessageDialog("Error", str(e), "❌", self).exec()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())
