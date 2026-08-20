from __future__ import annotations
"""Reusable card widgets — summary cards, quick actions, order cards."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES, CARD_RADIUS


class SummaryCard(QWidget):
    """Dashboard summary card with icon, label, and value."""

    def __init__(self, icon: str, label: str, value: str = "0",
                 icon_bg: str = None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(90)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface_container_lowest']};
                border: 1px solid {COLORS['surface_container_low']};
                border-radius: {CARD_RADIUS}px;
            }}
        """)
        self._setup_ui(icon, label, value, icon_bg)

    def _setup_ui(self, icon: str, label: str, value: str, icon_bg: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Icon
        bg_color = icon_bg or COLORS['surface_container_highest']
        icon_label = QLabel(icon)
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                border-radius: 8px;
                font-size: 22px;
                border: none;
            }}
        """)
        layout.addWidget(icon_label)

        # Text
        text_container = QWidget()
        text_container.setStyleSheet("border: none; background: transparent;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        label_widget = QLabel(label.upper())
        label_widget.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZES['label_sm']}px;
                font-weight: 500;
                color: {COLORS['on_surface_variant']};
                letter-spacing: 1px;
                border: none;
            }}
        """)
        text_layout.addWidget(label_widget)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZES['headline_lg']}px;
                font-weight: 600;
                color: {COLORS['on_surface']};
                border: none;
            }}
        """)
        text_layout.addWidget(self.value_label)

        layout.addWidget(text_container)
        layout.addStretch()

    def set_value(self, value: str):
        self.value_label.setText(value)


class QuickActionCard(QPushButton):
    """Dashboard quick action button."""

    def __init__(self, icon: str, label: str, primary: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 96)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 12, 8, 12)
        self._layout.setSpacing(8)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                border: none;
                background: transparent;
            }}
        """)
        self._layout.addWidget(icon_label)

        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        self._layout.addWidget(text_label)

        if primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    border: none;
                    border-radius: {CARD_RADIUS}px;
                    color: {COLORS['on_primary']};
                    font-size: {FONT_SIZES['label_sm']}px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['primary_container']};
                }}
                QLabel {{
                    color: {COLORS['on_primary']};
                    border: none;
                    background: transparent;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['surface_container_lowest']};
                    border: 1px solid {COLORS['surface_container_low']};
                    border-radius: {CARD_RADIUS}px;
                    color: {COLORS['on_surface']};
                    font-size: {FONT_SIZES['label_sm']}px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['surface_container']};
                }}
                QLabel {{
                    border: none;
                    background: transparent;
                }}
            """)


class StatusCountCard(QWidget):
    """Pipeline status count card used on dashboard."""

    def __init__(self, count: str, label: str, border_color: str = None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        border_top = f"border-top: 4px solid {border_color};" if border_color else ""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface_container_lowest']};
                border: 1px solid {COLORS['surface_container_low']};
                border-radius: {CARD_RADIUS}px;
                {border_top}
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.count_label = QLabel(count)
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZES['headline_md']}px;
                font-weight: 600;
                color: {COLORS['on_surface']};
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(self.count_label)

        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZES['label_sm']}px;
                font-weight: 500;
                color: {COLORS['on_surface_variant']};
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(label_widget)

    def set_count(self, count: str):
        self.count_label.setText(count)
