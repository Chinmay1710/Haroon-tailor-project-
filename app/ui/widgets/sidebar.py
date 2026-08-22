from __future__ import annotations
"""Sidebar navigation — fixed left panel matching the Stitch design."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QFrame, QSizePolicy)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont, QIcon
from app.ui.theme import COLORS, FONT_SIZES, SIDEBAR_WIDTH


class NavButton(QPushButton):
    """A single navigation button in the sidebar."""


    def __init__(self, icon_char: str, text: str, parent=None):
        super().__init__(parent)
        self.icon_char = icon_char
        self.nav_text = text
        self.setText(f"  {icon_char}    {text}")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self._active = False
        self._update_style()

    def set_active(self, active: bool):
        self._active = active
        self.setChecked(active)
        self._update_style()

    def _update_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(211, 228, 254, 0.1);
                    color: {COLORS['on_primary']};
                    border: none;
                    border-left: 4px solid {COLORS['surface_container_highest']};
                    border-radius: 8px;
                    font-size: {FONT_SIZES['label_lg']}px;
                    font-weight: 700;
                    text-align: left;
                    padding-left: 12px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: rgba(255, 255, 255, 0.7);
                    border: none;
                    border-left: 4px solid transparent;
                    border-radius: 8px;
                    font-size: {FONT_SIZES['label_lg']}px;
                    font-weight: 500;
                    text-align: left;
                    padding-left: 12px;
                }}
                QPushButton:hover {{
                    background-color: rgba(30, 41, 59, 0.2);
                    color: {COLORS['on_primary']};
                }}
            """)


class Sidebar(QWidget):
    """Fixed left navigation sidebar matching the Stitch design."""

    navigation_clicked = Signal(str)  # Emits the page name

    # Navigation items: (icon, label, page_key)
    NAV_ITEMS = [
        ("📊", "Dashboard", "dashboard"),
        ("👤", "Customers", "customers"),
        ("📏", "Measurements", "measurements"),
        ("🛍️", "Orders", "orders"),
        ("💳", "Payments", "payments"),
        ("📋", "Expenses", "expenses"),
        ("📈", "Reports", "reports"),
        ("⚙️", "Settings", "settings"),
    ]

    BOTTOM_ITEMS = [
        ("💾", "Backup & Restore", "backup"),
        ("❓", "Help", "help"),
        ("📡", "Offline Mode", "offline"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['primary']};
            }}
        """)
        self.nav_buttons: dict[str, NavButton] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 8)
        layout.setSpacing(0)

        # ─── Header ───
        header = QWidget()
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 16)
        header_layout.setSpacing(12)

        # Shop icon placeholder
        icon_label = QLabel("✂️")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['primary_container']};
                border-radius: 20px;
                font-size: 20px;
            }}
        """)
        header_layout.addWidget(icon_label)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        self.shop_name_label = QLabel("Tailor Shop")
        self.shop_name_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 700;
                color: {COLORS['on_primary']};
            }}
        """)
        title_layout.addWidget(self.shop_name_label)

        subtitle = QLabel("Manager")
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                color: rgba(255, 255, 255, 0.7);
            }}
        """)
        title_layout.addWidget(subtitle)

        header_layout.addWidget(title_container)
        header_layout.addStretch()

        layout.addWidget(header)

        # Divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: rgba(255,255,255,0.1);")
        layout.addWidget(divider)

        layout.addSpacing(8)

        # ─── Main Navigation ───
        for icon, label, key in self.NAV_ITEMS:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, k=key: self._on_nav_clicked(k))
            self.nav_buttons[key] = btn
            layout.addWidget(btn)
            layout.addSpacing(2)

        layout.addStretch()

        # ─── Bottom Section ───
        bottom_divider = QFrame()
        bottom_divider.setFixedHeight(1)
        bottom_divider.setStyleSheet("background-color: rgba(255,255,255,0.1);")
        layout.addWidget(bottom_divider)
        layout.addSpacing(8)

        for icon, label, key in self.BOTTOM_ITEMS:
            btn = NavButton(icon, label)
            if key == "offline":
                btn.setEnabled(False)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: rgba(255, 255, 255, 0.5);
                        border: none;
                        border-radius: 8px;
                        font-size: {FONT_SIZES['label_sm']}px;
                        font-weight: 500;
                        text-align: left;
                        padding-left: 16px;
                    }}
                """)
            else:
                btn.clicked.connect(lambda checked, k=key: self._on_nav_clicked(k))
                self.nav_buttons[key] = btn
            layout.addWidget(btn)
            layout.addSpacing(2)

    def _on_nav_clicked(self, page_key: str):
        self.set_active_page(page_key)
        self.navigation_clicked.emit(page_key)

    def set_active_page(self, page_key: str):
        for key, btn in self.nav_buttons.items():
            btn.set_active(key == page_key)

    def set_shop_name(self, name: str):
        self.shop_name_label.setText(name or "Tailor Shop")
