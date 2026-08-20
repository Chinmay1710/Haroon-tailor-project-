from __future__ import annotations
"""Customer dialog — Add/Edit customer form."""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QTextEdit, QPushButton, QFormLayout)
from PySide6.QtCore import Qt
from app.ui.theme import COLORS, FONT_SIZES, CARD_RADIUS
from app.utils.validators import validate_required, validate_mobile


class CustomerDialog(QDialog):
    """Dialog for adding or editing a customer."""

    def __init__(self, customer=None, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.result_data = None
        self.setWindowTitle("Edit Customer" if customer else "Add Customer")
        self.setFixedWidth(500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS['surface_container_lowest']}; }}
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Edit Customer" if self.customer else "Add New Customer")
        title.setStyleSheet(f"""
            font-size: {FONT_SIZES['headline_md']}px;
            font-weight: 600;
            color: {COLORS['primary']};
        """)
        layout.addWidget(title)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter customer name")
        self.name_input.setFixedHeight(42)
        form.addRow(self._label("Name *"), self.name_input)

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Enter mobile number")
        self.mobile_input.setFixedHeight(42)
        form.addRow(self._label("Mobile"), self.mobile_input)

        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter address")
        self.address_input.setMaximumHeight(80)
        form.addRow(self._label("Address"), self.address_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Any additional notes")
        self.notes_input.setMaximumHeight(80)
        form.addRow(self._label("Notes"), self.notes_input)

        layout.addLayout(form)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setProperty("cssClass", "error")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Customer")
        save_btn.setProperty("cssClass", "primary")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        # Pre-fill if editing
        if self.customer:
            self.name_input.setText(self.customer.name or "")
            self.mobile_input.setText(self.customer.mobile or "")
            self.address_input.setPlainText(self.customer.address or "")
            self.notes_input.setPlainText(self.customer.notes or "")

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            font-size: {FONT_SIZES['label_lg']}px;
            font-weight: 600;
            color: {COLORS['on_surface']};
        """)
        return lbl

    def _on_save(self):
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()

        # Validate
        err = validate_required("Name", name)
        if err:
            self._show_error(err)
            return
        err = validate_mobile(mobile)
        if err:
            self._show_error(err)
            return

        self.result_data = {
            "name": name,
            "mobile": mobile,
            "address": self.address_input.toPlainText().strip(),
            "notes": self.notes_input.toPlainText().strip(),
        }
        self.accept()

    def _show_error(self, msg: str):
        self.error_label.setText(msg)
        self.error_label.setVisible(True)
