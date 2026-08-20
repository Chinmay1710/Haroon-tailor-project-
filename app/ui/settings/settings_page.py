from __future__ import annotations
"""Settings page — shop information and app preferences."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QLineEdit, QTextEdit, QComboBox,
                                QCheckBox, QFormLayout, QScrollArea, QGroupBox)
from PySide6.QtCore import Qt
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG
from app.database.engine import get_session
from app.repositories.settings_repo import SettingsRepository
from app.ui.widgets.notification import show_toast


class SettingsPage(QWidget):
    """Settings page for shop info and preferences."""

    def __init__(self, parent=None):
        super().__init__(parent)
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

        title = QLabel("Settings")
        title.setStyleSheet(f"font-size: 32px; font-weight: 600; color: {COLORS['on_surface']};")
        layout.addWidget(title)

        # Shop Info
        shop_group = QGroupBox("🏪 Shop Information")
        shop_form = QFormLayout(shop_group)
        shop_form.setSpacing(12)

        self.shop_name_input = QLineEdit()
        self.shop_name_input.setFixedHeight(42)
        shop_form.addRow("Shop Name:", self.shop_name_input)

        self.owner_input = QLineEdit()
        self.owner_input.setFixedHeight(42)
        shop_form.addRow("Owner Name:", self.owner_input)

        self.phone_input = QLineEdit()
        self.phone_input.setFixedHeight(42)
        shop_form.addRow("Phone:", self.phone_input)

        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        shop_form.addRow("Address:", self.address_input)

        layout.addWidget(shop_group)

        # App Settings
        app_group = QGroupBox("⚙️ Application Settings")
        app_form = QFormLayout(app_group)
        app_form.setSpacing(12)

        self.currency_input = QComboBox()
        self.currency_input.addItems(["₹", "$", "€", "£", "¥"])
        self.currency_input.setEditable(True)
        self.currency_input.setFixedHeight(42)
        app_form.addRow("Currency:", self.currency_input)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["inches", "cm"])
        self.unit_combo.setFixedHeight(42)
        app_form.addRow("Measurement Unit:", self.unit_combo)

        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        self.date_format_combo.setFixedHeight(42)
        app_form.addRow("Date Format:", self.date_format_combo)

        layout.addWidget(app_group)

        # Printing
        print_group = QGroupBox("🖨️ Printing")
        print_form = QFormLayout(print_group)
        print_form.setSpacing(12)

        self.paper_combo = QComboBox()
        self.paper_combo.addItems(["A4", "A5", "Letter", "80mm (Thermal)"])
        self.paper_combo.setFixedHeight(42)
        print_form.addRow("Paper Size:", self.paper_combo)

        layout.addWidget(print_group)

        # Backup
        backup_group = QGroupBox("💾 Backup")
        backup_form = QFormLayout(backup_group)
        backup_form.setSpacing(12)

        self.backup_location_input = QLineEdit()
        self.backup_location_input.setFixedHeight(42)
        backup_form.addRow("Backup Location:", self.backup_location_input)

        self.auto_backup_check = QCheckBox("Enable automatic backup on exit")
        backup_form.addRow("", self.auto_backup_check)

        layout.addWidget(backup_group)

        # Save
        save_row = QHBoxLayout()
        save_row.addStretch()
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setProperty("cssClass", "primary")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedHeight(44)
        save_btn.clicked.connect(self._save)
        save_row.addWidget(save_btn)
        layout.addLayout(save_row)

        layout.addStretch()
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh_data(self):
        try:
            session = get_session()
            try:
                settings = SettingsRepository(session).get_settings()
                self.shop_name_input.setText(settings.shop_name or "")
                self.owner_input.setText(settings.owner_name or "")
                self.phone_input.setText(settings.phone or "")
                self.address_input.setPlainText(settings.address or "")
                self.currency_input.setCurrentText(settings.currency or "₹")
                self.unit_combo.setCurrentText(settings.measurement_unit or "inches")
                self.date_format_combo.setCurrentText(settings.date_format or "DD/MM/YYYY")
                self.paper_combo.setCurrentText(settings.receipt_paper_size or "A4")
                self.backup_location_input.setText(settings.backup_location or "")
                self.auto_backup_check.setChecked(settings.auto_backup or False)
            finally:
                session.close()
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Settings load error: {e}")

    def _save(self):
        try:
            session = get_session()
            try:
                SettingsRepository(session).update_settings(
                    shop_name=self.shop_name_input.text().strip(),
                    owner_name=self.owner_input.text().strip(),
                    phone=self.phone_input.text().strip(),
                    address=self.address_input.toPlainText().strip(),
                    currency=self.currency_input.currentText(),
                    measurement_unit=self.unit_combo.currentText(),
                    date_format=self.date_format_combo.currentText(),
                    receipt_paper_size=self.paper_combo.currentText(),
                    backup_location=self.backup_location_input.text().strip(),
                    auto_backup=self.auto_backup_check.isChecked(),
                )
                session.commit()
            finally:
                session.close()
            show_toast(self, "Settings saved successfully!", "success")
        except Exception as e:
            show_toast(self, "Failed to save settings", "error")
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Settings save error: {e}")
