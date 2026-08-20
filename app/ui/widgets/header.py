from __future__ import annotations
"""Header bar — top application bar with title, search, and actions."""

from datetime import datetime
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton,
                                QLineEdit, QSizePolicy)
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES, HEADER_HEIGHT, GUTTER


class Header(QWidget):
    """Top header bar matching the Stitch design."""

    new_order_clicked = Signal()
    search_submitted = Signal(str)
    notification_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(HEADER_HEIGHT)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border-bottom: 1px solid {COLORS['surface_container_low']};
            }}
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(GUTTER, 0, GUTTER, 0)
        layout.setSpacing(16)

        # Page title
        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZES['headline_md']}px;
                font-weight: 600;
                color: {COLORS['primary']};
                border: none;
            }}
        """)
        layout.addWidget(self.page_title)

        layout.addStretch()

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search orders, customers...")
        self.search_input.setFixedWidth(280)
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: 14px;
                padding: 8px 16px;
                border: 1px solid {COLORS['outline_variant']};
                border-radius: 20px;
                background-color: {COLORS['surface_container_low']};
                color: {COLORS['on_surface']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
                background-color: {COLORS['surface_container_lowest']};
            }}
        """)
        self.search_input.returnPressed.connect(
            lambda: self.search_submitted.emit(self.search_input.text())
        )
        layout.addWidget(self.search_input)

        # Date display
        self.date_label = QLabel()
        self._update_date()
        self.date_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZES['label_sm']}px;
                color: {COLORS['on_surface_variant']};
                padding: 8px;
                border: none;
            }}
        """)
        layout.addWidget(self.date_label)

        # Notification bell
        notif_btn = QPushButton("🔔")
        notif_btn.setFixedSize(40, 40)
        notif_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        notif_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 18px;
                border: none;
                border-radius: 20px;
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_container_low']};
            }}
        """)
        notif_btn.clicked.connect(self.notification_clicked.emit)
        layout.addWidget(notif_btn)

        # New Order button
        new_order_btn = QPushButton("  ＋  New Order")
        new_order_btn.setFixedHeight(40)
        new_order_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_order_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: {FONT_SIZES['label_lg']}px;
                font-weight: 600;
                padding: 0 20px;
                border: none;
                border-radius: 10px;
                background-color: {COLORS['primary']};
                color: {COLORS['on_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_container']};
            }}
            QPushButton:pressed {{
                background-color: #0d1f38;
            }}
        """)
        new_order_btn.clicked.connect(self.new_order_clicked.emit)
        layout.addWidget(new_order_btn)

    def _update_date(self):
        now = datetime.now()
        self.date_label.setText(now.strftime("📅 %a, %d %b %Y"))

    def set_title(self, title: str):
        self.page_title.setText(title)
