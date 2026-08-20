from __future__ import annotations
"""First-run setup wizard — initial shop configuration."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QLineEdit, QTextEdit)
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES
from app.database.engine import get_session
from app.repositories.settings_repo import SettingsRepository
from app.utils.validators import validate_required


class SetupWizard(QWidget):
    """First-run setup screen for shop information."""

    setup_completed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['surface']};")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Center container
        center = QWidget()
        center.setMaximumWidth(500)
        center.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface_container_lowest']};
                border-radius: 16px;
            }}
        """)

        form_layout = QVBoxLayout(center)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)

        # Icon
        icon = QLabel("✂️")
        icon.setStyleSheet("font-size: 48px; border: none; background: transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(icon)

        # Title
        title = QLabel("Welcome to Tailor Shop Manager")
        title.setStyleSheet(f"""
            font-size: {FONT_SIZES['headline_lg']}px;
            font-weight: 700;
            color: {COLORS['primary']};
            border: none; background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        form_layout.addWidget(title)

        subtitle = QLabel("Let's set up your shop. This only takes a minute.")
        subtitle.setStyleSheet(f"""
            font-size: {FONT_SIZES['body_md']}px;
            color: {COLORS['on_surface_variant']};
            border: none; background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(subtitle)

        form_layout.addSpacing(16)

        # Fields
        self.shop_name_input = self._create_field("Shop Name *", "Enter your shop name", form_layout)
        self.owner_input = self._create_field("Owner Name", "Enter owner name", form_layout)
        self.phone_input = self._create_field("Phone", "Enter phone number", form_layout)

        addr_label = QLabel("Address")
        addr_label.setStyleSheet(f"font-size: {FONT_SIZES['label_lg']}px; font-weight: 600; border: none; background: transparent;")
        form_layout.addWidget(addr_label)
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter shop address")
        self.address_input.setMaximumHeight(70)
        form_layout.addWidget(self.address_input)

        # Error
        self.error_label = QLabel()
        self.error_label.setProperty("cssClass", "error")
        self.error_label.setVisible(False)
        self.error_label.setStyleSheet(f"color: {COLORS['error']}; border: none; background: transparent;")
        form_layout.addWidget(self.error_label)

        # Start button
        start_btn = QPushButton("🚀  Start Using Tailor Shop Manager")
        start_btn.setProperty("cssClass", "primary")
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.setFixedHeight(52)
        start_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 18px; font-weight: 600;
                background-color: {COLORS['primary']};
                color: {COLORS['on_primary']};
                border: none; border-radius: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_container']};
            }}
        """)
        start_btn.clicked.connect(self._on_start)
        form_layout.addWidget(start_btn)

        # Center the form
        outer = QHBoxLayout()
        outer.addStretch()
        outer.addWidget(center)
        outer.addStretch()

        wrapper = QVBoxLayout()
        wrapper.addStretch()
        wrapper.addLayout(outer)
        wrapper.addStretch()

        layout.addLayout(wrapper)

    def _create_field(self, label_text: str, placeholder: str, parent_layout) -> QLineEdit:
        label = QLabel(label_text)
        label.setStyleSheet(f"font-size: {FONT_SIZES['label_lg']}px; font-weight: 600; border: none; background: transparent;")
        parent_layout.addWidget(label)
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(42)
        parent_layout.addWidget(inp)
        return inp

    def _on_start(self):
        shop_name = self.shop_name_input.text().strip()
        err = validate_required("Shop Name", shop_name)
        if err:
            self.error_label.setText(err)
            self.error_label.setVisible(True)
            return

        try:
            session = get_session()
            try:
                repo = SettingsRepository(session)
                repo.update_settings(
                    shop_name=shop_name,
                    owner_name=self.owner_input.text().strip(),
                    phone=self.phone_input.text().strip(),
                    address=self.address_input.toPlainText().strip(),
                    is_setup_done=True,
                )
                session.commit()
            finally:
                session.close()

            self.setup_completed.emit()
        except Exception as e:
            self.error_label.setText("Unable to save. Please try again.")
            self.error_label.setVisible(True)
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Setup error: {e}")
