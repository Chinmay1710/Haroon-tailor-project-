from __future__ import annotations
"""Measurement dialog — Add/Edit measurement profile with template-based fields."""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QTextEdit, QPushButton, QComboBox,
                                QFormLayout, QGridLayout, QScrollArea, QWidget,
                                QFrame, QButtonGroup)
from PySide6.QtCore import Qt
from app.ui.theme import COLORS, FONT_SIZES, CARD_RADIUS
from app.config import MEASUREMENT_TEMPLATES


class MeasurementDialog(QDialog):
    """Dialog for adding or editing a measurement profile."""

    def __init__(self, customer_id: int = None, customer_name: str = "",
                 profile=None, customers=None, parent=None):
        super().__init__(parent)
        self.customer_id = customer_id
        self.profile = profile
        self.customers = customers or []
        self.result_data = None
        self.measurement_inputs: dict[str, QLineEdit] = {}
        self.custom_fields: list[tuple[QLineEdit, QLineEdit]] = []
        
        self.setWindowTitle("Edit Measurement" if profile else "Add Measurement")
        self.setMinimumWidth(850)
        self.setMinimumHeight(650)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['surface']}; }}")
        self._setup_ui(customer_name)

    def _setup_ui(self, customer_name: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header area
        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title = QLabel("Edit Measurement" if self.profile else "Add Measurement")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_lg']}px; font-weight: 600; color: {COLORS['on_surface']};")
        title_col.addWidget(title)
        
        if not self.customer_id and self.customers:
            cust_row = QHBoxLayout()
            cust_label = QLabel("Customer:")
            cust_row.addWidget(cust_label)
            self.customer_combo = QComboBox()
            for c in self.customers:
                self.customer_combo.addItem(f"{c.name} (ID: {c.id})", c.id)
            self.customer_combo.setFixedHeight(36)
            cust_row.addWidget(self.customer_combo, 1)
            title_col.addLayout(cust_row)
        elif customer_name:
            cust_label = QLabel(f"Record new dimensions for {customer_name}")
            cust_label.setStyleSheet(f"font-size: {FONT_SIZES['body_md']}px; color: {COLORS['on_surface_variant']};")
            title_col.addWidget(cust_label)
            
        header_row.addLayout(title_col)
        header_row.addStretch()
        
        # Unit toggle
        unit_container = QFrame()
        unit_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface_container']};
                border: 1px solid {COLORS['outline_variant']};
                border-radius: 8px;
            }}
        """)
        unit_layout = QHBoxLayout(unit_container)
        unit_layout.setContentsMargins(4, 4, 4, 4)
        unit_layout.setSpacing(4)
        
        self.unit_group = QButtonGroup(self)
        
        self.btn_inches = QPushButton("Inches")
        self.btn_inches.setCheckable(True)
        self.btn_inches.setChecked(True)
        self.btn_inches.setFixedHeight(36)
        
        self.btn_cm = QPushButton("CM")
        self.btn_cm.setCheckable(True)
        self.btn_cm.setFixedHeight(36)
        
        self.unit_group.addButton(self.btn_inches)
        self.unit_group.addButton(self.btn_cm)
        
        for btn in (self.btn_inches, self.btn_cm):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: {FONT_SIZES['label_lg']}px; font-weight: 600;
                    background-color: transparent; border: none; border-radius: 6px;
                    color: {COLORS['on_surface_variant']}; padding: 0 16px;
                }}
                QPushButton:checked {{
                    background-color: {COLORS['surface']}; color: {COLORS['primary']};
                }}
            """)
            unit_layout.addWidget(btn)
            
        header_row.addWidget(unit_container)
        layout.addLayout(header_row)

        # Name row
        name_row = QHBoxLayout()
        name_label = QLabel("Profile Name:")
        name_label.setStyleSheet(f"font-size: {FONT_SIZES['label_lg']}px; font-weight: 600;")
        name_row.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Regular Fit")
        self.name_input.setFixedHeight(40)
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['surface_container_low']};
                border: 1px solid {COLORS['outline_variant']};
                border-radius: 8px; padding: 0 12px;
                font-size: {FONT_SIZES['body_md']}px;
            }}
            QLineEdit:focus {{ border: 1px solid {COLORS['primary']}; }}
        """)
        name_row.addWidget(self.name_input, 1)
        layout.addLayout(name_row)

        # Main Split area
        split_layout = QHBoxLayout()
        split_layout.setSpacing(24)

        # Left Column: Templates
        left_col = QFrame()
        left_col.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface_container_lowest']};
                border: 1px solid {COLORS['outline_variant']};
                border-radius: {CARD_RADIUS}px;
            }}
        """)
        left_col.setFixedWidth(240)
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(16, 20, 16, 20)
        left_layout.setSpacing(8)
        
        tmpl_label = QLabel("Template")
        tmpl_label.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; color: {COLORS['on_background']}; border: none;")
        left_layout.addWidget(tmpl_label)
        left_layout.addSpacing(8)
        
        self.template_group = QButtonGroup(self)
        self.template_group.buttonClicked.connect(self._on_template_clicked)
        
        icons = {"Shirt": "👕", "Pant": "👖", "Kurta": "👘", "Blouse": "👚", "Suit": "👔", "Custom": "✏️"}
        
        self.current_template = "Shirt"
        for tmpl in list(MEASUREMENT_TEMPLATES.keys()):
            btn = QPushButton(f"{icons.get(tmpl, '📐')}  {tmpl}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(44)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left; padding-left: 12px; border-radius: 8px; border: 1px solid transparent;
                    background-color: transparent; color: {COLORS['on_surface_variant']};
                    font-size: {FONT_SIZES['body_md']}px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['surface_container_low']}; color: {COLORS['on_surface']};
                }}
                QPushButton:checked {{
                    background-color: {COLORS['surface_container_high']};
                    border: 1px solid {COLORS['primary']};
                    color: {COLORS['primary']}; font-weight: 600;
                }}
            """)
            if tmpl == "Shirt":
                btn.setChecked(True)
            self.template_group.addButton(btn)
            left_layout.addWidget(btn)
            
            if tmpl == "Suit":
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setStyleSheet(f"background-color: {COLORS['outline_variant']}; border: none;")
                line.setFixedHeight(1)
                left_layout.addWidget(line)
        
        left_layout.addStretch()
        split_layout.addWidget(left_col)

        # Right Column: Fields
        right_col = QFrame()
        right_col.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface_container_lowest']};
                border: 1px solid {COLORS['outline_variant']};
                border-radius: {CARD_RADIUS}px;
            }}
        """)
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(24, 24, 24, 24)
        
        self.template_title = QLabel("Shirt Measurements")
        self.template_title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; border: none;")
        right_layout.addWidget(self.template_title)
        
        # Scroll area for fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.fields_container = QWidget()
        self.fields_container.setStyleSheet("background: transparent;")
        self.fields_layout = QGridLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 16, 0, 16)
        self.fields_layout.setSpacing(16)
        
        scroll.setWidget(self.fields_container)
        right_layout.addWidget(scroll, 1)
        
        # Notes
        notes_label = QLabel("Measurement Notes")
        notes_label.setStyleSheet(f"font-size: {FONT_SIZES['label_lg']}px; font-weight: 600; border: none;")
        right_layout.addWidget(notes_label)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Add specific fit preferences, body anomalies, or client requests here...")
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['surface_container_low']};
                border: 1px solid {COLORS['outline_variant']};
                border-radius: 8px; padding: 12px;
                font-size: {FONT_SIZES['body_md']}px;
            }}
            QTextEdit:focus {{ border: 1px solid {COLORS['primary']}; }}
        """)
        right_layout.addWidget(self.notes_input)
        
        # Actions
        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 16, 0, 0)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLORS['error']}; border: none;")
        self.error_label.setVisible(False)
        actions_row.addWidget(self.error_label)
        actions_row.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setFixedHeight(44)
        cancel_btn.setFixedWidth(120)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLORS['outline_variant']}; background-color: {COLORS['surface']};
                border-radius: 8px; font-size: {FONT_SIZES['label_lg']}px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {COLORS['surface_container_low']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        actions_row.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Measurement")
        save_btn.setProperty("cssClass", "primary")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedHeight(44)
        save_btn.setFixedWidth(180)
        save_btn.clicked.connect(self._on_save)
        actions_row.addWidget(save_btn)
        
        right_layout.addLayout(actions_row)
        split_layout.addWidget(right_col, 1)
        layout.addLayout(split_layout)

        # Initialize Data
        if self.profile:
            # Set template
            for btn in self.template_group.buttons():
                if self.profile.template_type in btn.text():
                    btn.setChecked(True)
                    self.current_template = self.profile.template_type
                    break
                    
            self.name_input.setText(self.profile.name)
            
            if self.profile.unit.lower() == "cm":
                self.btn_cm.setChecked(True)
            else:
                self.btn_inches.setChecked(True)
                
            self.notes_input.setPlainText(self.profile.notes or "")
            self._build_fields(self.current_template)
            
            for val in self.profile.values:
                if val.field_name in self.measurement_inputs:
                    self.measurement_inputs[val.field_name].setText(val.field_value or "")
        else:
            self._build_fields("Shirt")

    def _on_template_clicked(self, button: QPushButton):
        tmpl = button.text().split("  ")[-1].strip()
        self.current_template = tmpl
        self.template_title.setText(f"{tmpl} Measurements")
        self._build_fields(tmpl)

    def _build_fields(self, template: str):
        while self.fields_layout.count():
            child = self.fields_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.measurement_inputs.clear()
        self.custom_fields.clear()

        fields = MEASUREMENT_TEMPLATES.get(template, [])

        if template == "Custom":
            self._build_custom_fields()
            return

        for i, field_name in enumerate(fields):
            col = i % 3
            row = i // 3

            field_container = QWidget()
            field_container.setStyleSheet("background: transparent;")
            flayout = QVBoxLayout(field_container)
            flayout.setContentsMargins(0, 0, 0, 0)
            flayout.setSpacing(4)
            
            label = QLabel(field_name)
            label.setStyleSheet(f"font-size: {FONT_SIZES['label_lg']}px; font-weight: 600; border: none; color: {COLORS['on_surface']};")
            flayout.addWidget(label)

            inp_container = QWidget()
            inp_container.setStyleSheet("background: transparent;")
            inp_layout = QHBoxLayout(inp_container)
            inp_layout.setContentsMargins(0, 0, 0, 0)
            inp_layout.setSpacing(0)
            
            inp = QLineEdit()
            inp.setPlaceholderText("00.0")
            inp.setFixedHeight(48)
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLORS['surface_container_low']};
                    border: 1px solid {COLORS['outline_variant']};
                    border-radius: 8px; padding: 0 40px 0 16px;
                    font-size: {FONT_SIZES['headline_md']}px; text-align: center;
                }}
                QLineEdit:focus {{ border: 1px solid {COLORS['primary']}; }}
            """)
            inp_layout.addWidget(inp)
            
            unit_lbl = QLabel("in" if self.btn_inches.isChecked() else "cm")
            unit_lbl.setStyleSheet(f"font-size: {FONT_SIZES['label_sm']}px; color: {COLORS['on_surface_variant']}; border: none; background: transparent;")
            
            # Use absolute positioning for the unit label inside QLineEdit using layouts
            # (In PySide, an easier way is to add it via a container or QAction, but we'll use a tight layout)
            
            self.fields_layout.addWidget(field_container, row, col)
            self.measurement_inputs[field_name] = inp

    def _build_custom_fields(self):
        add_btn = QPushButton("+ Add Field")
        add_btn.setProperty("cssClass", "text")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_custom_field)
        self.fields_layout.addWidget(add_btn, 0, 0, 1, 3)
        self._add_custom_field()

    def _add_custom_field(self):
        row = len(self.custom_fields) + 1
        name_inp = QLineEdit()
        name_inp.setPlaceholderText("Field name")
        name_inp.setFixedHeight(40)
        self.fields_layout.addWidget(name_inp, row, 0)

        value_inp = QLineEdit()
        value_inp.setPlaceholderText("Value")
        value_inp.setFixedHeight(40)
        self.fields_layout.addWidget(value_inp, row, 1)

        self.custom_fields.append((name_inp, value_inp))

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("Profile Name is required")
            self.error_label.setVisible(True)
            return

        cust_id = self.customer_id
        if not cust_id and hasattr(self, 'customer_combo'):
            cust_id = self.customer_combo.currentData()
        if not cust_id:
            self.error_label.setText("Customer is required")
            self.error_label.setVisible(True)
            return

        values = {}
        if self.current_template == "Custom":
            for name_inp, value_inp in self.custom_fields:
                fn = name_inp.text().strip()
                fv = value_inp.text().strip()
                if fn:
                    values[fn] = fv
        else:
            for field_name, inp in self.measurement_inputs.items():
                values[field_name] = inp.text().strip()

        unit = "inches" if self.btn_inches.isChecked() else "cm"

        self.result_data = {
            "customer_id": cust_id,
            "template_type": self.current_template,
            "name": name,
            "unit": unit,
            "notes": self.notes_input.toPlainText().strip(),
            "values": values,
        }
        self.accept()
