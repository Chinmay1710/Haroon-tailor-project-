from __future__ import annotations
"""Status badge — pill-shaped status indicators."""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from app.ui.theme import STATUS_COLORS, FONT_SIZES


class StatusBadge(QLabel):
    """Pill-shaped status badge with status-specific colors."""

    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.set_status(status)

    def set_status(self, status: str):
        text_color, bg_color = STATUS_COLORS.get(status, ("#6b7280", "#f3f4f6"))
        self.setText(status.title())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                font-size: {FONT_SIZES['label_sm'] - 1}px;
                font-weight: 600;
                padding: 4px 12px;
                border-radius: 12px;
                border: none;
            }}
        """)
        self.setFixedHeight(24)
        self.adjustSize()
