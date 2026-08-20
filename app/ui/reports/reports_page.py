from __future__ import annotations
"""Reports page — date-filtered business reports."""

from datetime import date, timedelta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QDateEdit, QScrollArea, QGridLayout)
from PySide6.QtCore import Signal, Qt, QDate
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG, STACK_MD, CARD_RADIUS
from app.ui.widgets.cards import SummaryCard
from app.services.report_service import ReportService
from app.utils.formatters import format_currency, format_date_display


class ReportsPage(QWidget):
    """Reports page with date filters and metric cards."""
    print_report = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.report_service = ReportService()
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

        title = QLabel("Reports")
        title.setStyleSheet(f"font-size: 32px; font-weight: 600; color: {COLORS['on_surface']};")
        layout.addWidget(title)

        # Date filters
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        self.filter_btns = {}
        for label in ["Today", "This Week", "This Month", "Custom"]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(36)
            btn.clicked.connect(lambda checked, l=label: self._apply_filter(l))
            self.filter_btns[label] = btn
            filter_row.addWidget(btn)

        filter_row.addSpacing(16)
        filter_row.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedHeight(36)
        filter_row.addWidget(self.start_date)
        filter_row.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedHeight(36)
        filter_row.addWidget(self.end_date)

        apply_btn = QPushButton("Apply")
        apply_btn.setProperty("cssClass", "primary")
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setFixedHeight(36)
        apply_btn.clicked.connect(self._load_custom)
        filter_row.addWidget(apply_btn)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        # Metric cards grid
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(STACK_MD)

        self.total_sales_card = SummaryCard("💰", "Total Sales", "₹0", COLORS['tertiary_fixed'])
        self.total_orders_card = SummaryCard("🛍️", "Total Orders", "0", COLORS['surface_container_highest'])
        self.completed_card = SummaryCard("✅", "Completed Orders", "0", "#ecfdf5")
        self.pending_card = SummaryCard("⏳", "Pending Payments", "₹0", COLORS['error_container'])
        self.expenses_card = SummaryCard("📋", "Total Expenses", "₹0", "#fff7ed")
        self.profit_card = SummaryCard("📊", "Estimated Profit", "₹0", "#ecfdf5")

        self.cards_grid.addWidget(self.total_sales_card, 0, 0)
        self.cards_grid.addWidget(self.total_orders_card, 0, 1)
        self.cards_grid.addWidget(self.completed_card, 0, 2)
        self.cards_grid.addWidget(self.pending_card, 1, 0)
        self.cards_grid.addWidget(self.expenses_card, 1, 1)
        self.cards_grid.addWidget(self.profit_card, 1, 2)
        layout.addLayout(self.cards_grid)

        # Period label
        self.period_label = QLabel("")
        self.period_label.setStyleSheet(f"font-size: {FONT_SIZES['body_md']}px; color: {COLORS['on_surface_variant']};")
        layout.addWidget(self.period_label)

        # Actions
        action_row = QHBoxLayout()
        action_row.addStretch()
        print_btn = QPushButton("🖨️ Print Report")
        print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        print_btn.clicked.connect(self._print_report)
        action_row.addWidget(print_btn)
        pdf_btn = QPushButton("📄 Export PDF")
        pdf_btn.setProperty("cssClass", "primary")
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.clicked.connect(self._print_report)
        action_row.addWidget(pdf_btn)
        layout.addLayout(action_row)

        layout.addStretch()
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.filter_btns["Today"].setChecked(True)
        self._style_filters()

    def _style_filters(self):
        for name, btn in self.filter_btns.items():
            if btn.isChecked():
                btn.setStyleSheet(f"""
                    QPushButton {{ background-color: {COLORS['primary']}; color: {COLORS['on_primary']};
                    border: none; border-radius: 18px; padding: 0 16px;
                    font-size: {FONT_SIZES['label_sm']}px; font-weight: 600; }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{ background-color: {COLORS['surface_container_lowest']};
                    color: {COLORS['on_surface_variant']};
                    border: 1px solid {COLORS['outline_variant']}; border-radius: 18px;
                    padding: 0 16px; font-size: {FONT_SIZES['label_sm']}px; }}
                    QPushButton:hover {{ background-color: {COLORS['surface_container_low']}; }}
                """)

    def _apply_filter(self, label: str):
        for name, btn in self.filter_btns.items():
            btn.setChecked(name == label)
        self._style_filters()

        today = date.today()
        if label == "Today":
            self._load_report(today, today)
        elif label == "This Week":
            start = today - timedelta(days=today.weekday())
            self._load_report(start, today)
        elif label == "This Month":
            self._load_report(today.replace(day=1), today)

    def _load_custom(self):
        sd = self.start_date.date()
        ed = self.end_date.date()
        self._load_report(
            date(sd.year(), sd.month(), sd.day()),
            date(ed.year(), ed.month(), ed.day()),
        )

    def _load_report(self, start: date, end: date):
        try:
            from app.database.engine import get_session
            from app.repositories.settings_repo import SettingsRepository
            session = get_session()
            try:
                currency = SettingsRepository(session).get_settings().currency or "₹"
            finally:
                session.close()

            self._current_data = self.report_service.get_report_data(start, end)
            d = self._current_data
            self.total_sales_card.set_value(format_currency(d["total_sales"], currency))
            self.total_orders_card.set_value(str(d["total_orders"]))
            self.completed_card.set_value(str(d["completed_orders"]))
            self.pending_card.set_value(format_currency(d["pending_payments"], currency))
            self.expenses_card.set_value(format_currency(d["total_expenses"], currency))
            self.profit_card.set_value(format_currency(d["estimated_profit"], currency))
            self.period_label.setText(
                f"Report period: {format_date_display(start)} — {format_date_display(end)}"
            )
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Report error: {e}")

    def refresh_data(self):
        self._apply_filter("Today")

    def _print_report(self):
        if hasattr(self, '_current_data'):
            self.print_report.emit(self._current_data)
