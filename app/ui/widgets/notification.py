from __future__ import annotations
"""Toast notifications — slide-in feedback messages."""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from app.ui.theme import COLORS, FONT_SIZES

TOAST_COLORS = {
    "success": ("#10b981", "#ecfdf5", "✅"),
    "error": ("#ef4444", "#fef2f2", "❌"),
    "info": ("#3b82f6", "#eff6ff", "ℹ️"),
    "warning": ("#f59e0b", "#fffbeb", "⚠️"),
}


class ToastNotification(QWidget):
    """Toast notification that appears at the top-right and auto-dismisses."""

    def __init__(self, message: str, toast_type: str = "info", duration: int = 3000, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(380)

        accent, bg, icon = TOAST_COLORS.get(toast_type, TOAST_COLORS["info"])

        container = QWidget(self)
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                border: 1px solid {accent};
                border-left: 4px solid {accent};
                border-radius: 10px;
            }}
        """)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px; border: none; background: transparent;")
        layout.addWidget(icon_label)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZES['body_md']}px;
                color: {COLORS['on_surface']};
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(msg_label, 1)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLORS['on_surface_variant']};
                font-size: 14px;
            }}
            QPushButton:hover {{
                color: {COLORS['on_surface']};
            }}
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        # Auto dismiss
        QTimer.singleShot(duration, self.close)

    def show_at(self, x: int, y: int):
        self.move(x, y)
        self.show()


def show_toast(parent_widget: QWidget, message: str, toast_type: str = "info", duration: int = 3000):
    """Convenience function to show a toast notification."""
    toast = ToastNotification(message, toast_type, duration, parent_widget)
    # Position at top-right of parent
    if parent_widget:
        parent_rect = parent_widget.geometry()
        x = parent_rect.right() - 400
        y = parent_rect.top() + 80
        toast.show_at(x, y)
    else:
        toast.show()
    return toast
