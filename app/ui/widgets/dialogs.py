from __future__ import annotations
"""Dialog helpers — confirmation and message dialogs."""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QWidget)
from PySide6.QtCore import Qt
from app.ui.theme import COLORS, FONT_SIZES, CARD_RADIUS


class ConfirmDialog(QDialog):
    """Confirmation dialog — 'Are you sure?' with Cancel/Confirm."""

    def __init__(self, title: str, message: str, confirm_text: str = "Confirm",
                 danger: bool = False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['surface_container_lowest']};
                border-radius: {CARD_RADIUS}px;
            }}
        """)
        self._setup_ui(title, message, confirm_text, danger)

    def _setup_ui(self, title: str, message: str, confirm_text: str, danger: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZES['headline_md']}px;
                font-weight: 600;
                color: {COLORS['on_surface']};
            }}
        """)
        layout.addWidget(title_label)

        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZES['body_md']}px;
                color: {COLORS['on_surface_variant']};
                line-height: 24px;
            }}
        """)
        layout.addWidget(msg_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if danger:
            confirm_btn.setProperty("cssClass", "danger")
        else:
            confirm_btn.setProperty("cssClass", "primary")
        confirm_btn.clicked.connect(self.accept)
        btn_layout.addWidget(confirm_btn)

        layout.addLayout(btn_layout)


class MessageDialog(QDialog):
    """Simple message dialog with OK button."""

    def __init__(self, title: str, message: str, icon: str = "ℹ️", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['surface_container_lowest']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Icon + Title
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        header.addWidget(icon_label)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: {FONT_SIZES['headline_md']}px;
            font-weight: 600;
            color: {COLORS['on_surface']};
        """)
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)

        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"""
            font-size: {FONT_SIZES['body_md']}px;
            color: {COLORS['on_surface_variant']};
        """)
        layout.addWidget(msg_label)

        # OK button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setProperty("cssClass", "primary")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)
