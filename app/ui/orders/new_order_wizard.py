from __future__ import annotations
"""New Order Wizard — multi-step guided order creation."""

from datetime import date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QLineEdit, QTextEdit, QComboBox,
                                QDateEdit, QStackedWidget, QScrollArea,
                                QFormLayout, QGridLayout, QFrame)
from PySide6.QtCore import Signal, Qt, QDate
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG, STACK_MD, CARD_RADIUS
from app.config import MEASUREMENT_TEMPLATES, PAYMENT_METHODS
from app.services.customer_service import CustomerService
from app.services.measurement_service import MeasurementService
from app.services.order_service import OrderService
from app.utils.formatters import format_currency, format_date_display
from app.utils.validators import validate_required, validate_positive_int, validate_amount, validate_advance


class NewOrderWizard(QWidget):
    """Multi-step order creation wizard."""

    order_created = Signal(object)  # Order object
    cancelled = Signal()
    print_receipt_requested = Signal(int)  # order_id
    print_slip_requested = Signal(int)
    view_order_requested = Signal(int)

    STEPS = ["Customer", "Clothing", "Measurement", "Details", "Payment", "Confirm"]

    def __init__(self, preselect_customer_id: int = None, parent=None):
        super().__init__(parent)
        self.customer_service = CustomerService()
        self.measurement_service = MeasurementService()
        self.order_service = OrderService()

        self.selected_customer = None
        self.selected_clothing = None
        self.selected_measurement_id = None
        self.preselect_customer_id = preselect_customer_id
        self.created_order = None

        self._setup_ui()
        if preselect_customer_id:
            self.selected_customer = self.customer_service.get_customer(preselect_customer_id)
            if self.selected_customer:
                self._go_to_step(1)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(CONTAINER_PADDING, 20, CONTAINER_PADDING, 20)
        layout.setSpacing(STACK_LG)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton("← Cancel")
        back_btn.setProperty("cssClass", "text")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.cancelled.emit)
        header.addWidget(back_btn)
        header.addStretch()
        title = QLabel("New Order")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_lg']}px; font-weight: 600; color: {COLORS['primary']};")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(QWidget())  # spacer
        layout.addLayout(header)

        # Progress indicator
        self.progress_layout = QHBoxLayout()
        self.progress_layout.setSpacing(0)
        self.step_indicators = []
        for i, step_name in enumerate(self.STEPS):
            indicator = self._create_step_indicator(i + 1, step_name)
            self.step_indicators.append(indicator)
            self.progress_layout.addWidget(indicator, 1)
        layout.addLayout(self.progress_layout)

        # Stacked content
        self.stack = QStackedWidget()
        self.stack.addWidget(self._create_step1_customer())
        self.stack.addWidget(self._create_step2_clothing())
        self.stack.addWidget(self._create_step3_measurement())
        self.stack.addWidget(self._create_step4_details())
        self.stack.addWidget(self._create_step5_payment())
        self.stack.addWidget(self._create_step6_confirm())
        layout.addWidget(self.stack, 1)

        self.current_step = 0
        self._update_progress()

    def _create_step_indicator(self, number: int, label: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setSpacing(4)
        circle = QLabel(str(number))
        circle.setFixedSize(32, 32)
        circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circle.setObjectName(f"step_circle_{number}")
        l.addWidget(circle, 0, Qt.AlignmentFlag.AlignCenter)
        text = QLabel(label)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setObjectName(f"step_text_{number}")
        text.setStyleSheet(f"font-size: {FONT_SIZES['label_sm']}px;")
        l.addWidget(text)
        return w

    def _update_progress(self):
        for i in range(len(self.STEPS)):
            circle = self.step_indicators[i].findChild(QLabel, f"step_circle_{i + 1}")
            text = self.step_indicators[i].findChild(QLabel, f"step_text_{i + 1}")
            if i < self.current_step:
                circle.setStyleSheet(f"""
                    background-color: {COLORS['primary']};
                    color: {COLORS['on_primary']};
                    border-radius: 16px;
                    font-weight: 700; font-size: 14px;
                """)
                text.setStyleSheet(f"font-size: 12px; color: {COLORS['primary']}; font-weight: 600;")
            elif i == self.current_step:
                circle.setStyleSheet(f"""
                    background-color: {COLORS['primary']};
                    color: {COLORS['on_primary']};
                    border-radius: 16px;
                    font-weight: 700; font-size: 14px;
                    border: 3px solid {COLORS['surface']};
                """)
                text.setStyleSheet(f"font-size: 12px; color: {COLORS['primary']}; font-weight: 600;")
            else:
                circle.setStyleSheet(f"""
                    background-color: {COLORS['surface_container_highest']};
                    color: {COLORS['primary']};
                    border-radius: 16px;
                    font-weight: 600; font-size: 14px;
                """)
                text.setStyleSheet(f"font-size: 12px; color: {COLORS['on_surface_variant']};")

    # ─── Step 1: Customer Selection ───
    def _create_step1_customer(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        title = QLabel("Select Customer")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; color: {COLORS['primary']};")
        layout.addWidget(title)

        self.cust_search = QLineEdit()
        self.cust_search.setPlaceholderText("🔍  Search by name or phone...")
        self.cust_search.setFixedHeight(44)
        self.cust_search.textChanged.connect(self._refresh_customer_list)
        layout.addWidget(self.cust_search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        self.cust_list_widget = QWidget()
        self.cust_list_layout = QVBoxLayout(self.cust_list_widget)
        self.cust_list_layout.setSpacing(8)
        scroll.setWidget(self.cust_list_widget)
        layout.addWidget(scroll, 1)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        self.step1_next = QPushButton("Continue to Clothing →")
        self.step1_next.setProperty("cssClass", "primary")
        self.step1_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.step1_next.setFixedHeight(44)
        self.step1_next.setEnabled(False)
        self.step1_next.clicked.connect(lambda: self._go_to_step(1))
        footer.addWidget(self.step1_next)
        layout.addLayout(footer)

        return page

    def _refresh_customer_list(self):
        while self.cust_list_layout.count():
            child = self.cust_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add new customer button
        add_btn = QPushButton("  ＋  Add New Customer")
        add_btn.setFixedHeight(60)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                border: 2px dashed {COLORS['outline_variant']};
                border-radius: {CARD_RADIUS}px;
                color: {COLORS['on_surface_variant']};
                font-size: {FONT_SIZES['label_lg']}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border-color: {COLORS['primary']};
                color: {COLORS['primary']};
                background-color: {COLORS['surface_container_low']};
            }}
        """)
        add_btn.clicked.connect(self._add_new_customer)
        self.cust_list_layout.addWidget(add_btn)

        # Search and list customers
        query = self.cust_search.text().strip()
        try:
            if query:
                customers = self.customer_service.search_customers(query)
            else:
                customers = self.customer_service.get_all_customers()

            for cust in customers[:20]:  # limit display
                card = QPushButton()
                card.setFixedHeight(60)
                card.setCursor(Qt.CursorShape.PointingHandCursor)
                card.setText(f"  {cust.name}\n  📱 {cust.mobile or 'No phone'}")
                card.setStyleSheet(f"""
                    QPushButton {{
                        text-align: left;
                        border: 1px solid {COLORS['outline_variant']};
                        border-radius: {CARD_RADIUS}px;
                        padding: 8px 16px;
                        font-size: 14px;
                        background: {COLORS['surface']};
                    }}
                    QPushButton:hover {{
                        border-color: {COLORS['primary']};
                        background: {COLORS['surface_container_low']};
                    }}
                """)
                cid = cust.id
                card.clicked.connect(lambda checked, c=cust: self._select_customer(c))
                self.cust_list_layout.addWidget(card)
        except Exception:
            pass

        self.cust_list_layout.addStretch()

    def _select_customer(self, customer):
        self.selected_customer = customer
        self.step1_next.setEnabled(True)
        self.step1_next.setText(f"Continue with {customer.name} →")

    def _add_new_customer(self):
        from app.ui.customers.customer_dialog import CustomerDialog
        dlg = CustomerDialog(parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted and dlg.result_data:
            try:
                customer = self.customer_service.create_customer(**dlg.result_data)
                self._select_customer(customer)
                self._go_to_step(1)
            except Exception as e:
                from app.utils.logger import get_logger
                get_logger(__name__).error(f"Create customer error: {e}")

    # ─── Step 2: Clothing Type ───
    def _create_step2_clothing(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        title = QLabel("Select Clothing Type")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; color: {COLORS['primary']};")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)
        clothing_types = ["Shirt", "Pant", "Kurta", "Blouse", "Suit", "Custom"]
        icons = ["👔", "👖", "🥻", "👗", "🤵", "✂️"]
        self.clothing_buttons = {}
        for i, (ct, icon) in enumerate(zip(clothing_types, icons)):
            btn = QPushButton(f"{icon}\n{ct}")
            btn.setFixedHeight(100)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 16px; font-weight: 600;
                    border: 2px solid {COLORS['outline_variant']};
                    border-radius: {CARD_RADIUS}px;
                    background: {COLORS['surface_container_lowest']};
                }}
                QPushButton:hover {{
                    border-color: {COLORS['primary']};
                    background: {COLORS['surface_container_low']};
                }}
                QPushButton:checked {{
                    border-color: {COLORS['primary']};
                    background: {COLORS['surface_container']};
                    color: {COLORS['primary']};
                }}
            """)
            btn.clicked.connect(lambda checked, c=ct: self._select_clothing(c))
            self.clothing_buttons[ct] = btn
            grid.addWidget(btn, i // 3, i % 3)
        layout.addLayout(grid)
        layout.addStretch()

        footer = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setProperty("cssClass", "text")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self._go_to_step(0))
        footer.addWidget(back_btn)
        footer.addStretch()
        self.step2_next = QPushButton("Continue to Measurement →")
        self.step2_next.setProperty("cssClass", "primary")
        self.step2_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.step2_next.setFixedHeight(44)
        self.step2_next.setEnabled(False)
        self.step2_next.clicked.connect(lambda: self._go_to_step(2))
        footer.addWidget(self.step2_next)
        layout.addLayout(footer)
        return page

    def _select_clothing(self, clothing_type: str):
        self.selected_clothing = clothing_type
        for name, btn in self.clothing_buttons.items():
            btn.setChecked(name == clothing_type)
        self.step2_next.setEnabled(True)

    # ─── Step 3: Measurement Selection ───
    def _create_step3_measurement(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        title = QLabel("Select Measurement")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; color: {COLORS['primary']};")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        self.meas_list_widget = QWidget()
        self.meas_list_layout = QVBoxLayout(self.meas_list_widget)
        self.meas_list_layout.setSpacing(8)
        scroll.setWidget(self.meas_list_widget)
        layout.addWidget(scroll, 1)

        footer = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setProperty("cssClass", "text")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self._go_to_step(1))
        footer.addWidget(back_btn)
        footer.addStretch()
        self.step3_next = QPushButton("Continue to Details →")
        self.step3_next.setProperty("cssClass", "primary")
        self.step3_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.step3_next.setFixedHeight(44)
        self.step3_next.clicked.connect(lambda: self._go_to_step(3))
        footer.addWidget(self.step3_next)
        layout.addLayout(footer)
        return page

    def _refresh_measurement_list(self):
        while self.meas_list_layout.count():
            child = self.meas_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add new measurement button
        add_btn = QPushButton("  ＋  Create New Measurement")
        add_btn.setFixedHeight(50)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                border: 2px dashed {COLORS['outline_variant']};
                border-radius: {CARD_RADIUS}px;
                color: {COLORS['on_surface_variant']};
                font-size: {FONT_SIZES['label_lg']}px;
            }}
            QPushButton:hover {{ border-color: {COLORS['primary']}; color: {COLORS['primary']}; }}
        """)
        add_btn.clicked.connect(self._add_new_measurement)
        self.meas_list_layout.addWidget(add_btn)

        # List existing measurements for this customer
        if self.selected_customer:
            profiles = self.measurement_service.get_profiles_for_customer(self.selected_customer.id)
            for prof in profiles:
                card = QPushButton()
                card.setFixedHeight(60)
                card.setCursor(Qt.CursorShape.PointingHandCursor)
                card.setCheckable(True)
                values_preview = ", ".join(f"{v.field_name}: {v.field_value}" for v in prof.values[:4] if v.field_value)
                card.setText(f"  📏 {prof.name} ({prof.template_type})\n  {values_preview}")
                card.setStyleSheet(f"""
                    QPushButton {{
                        text-align: left;
                        border: 1px solid {COLORS['outline_variant']};
                        border-radius: {CARD_RADIUS}px;
                        padding: 8px 16px;
                        font-size: 13px;
                        background: {COLORS['surface']};
                    }}
                    QPushButton:hover {{ border-color: {COLORS['primary']}; }}
                    QPushButton:checked {{
                        border: 2px solid {COLORS['primary']};
                        background: {COLORS['surface_container_low']};
                    }}
                """)
                pid = prof.id
                card.clicked.connect(lambda checked, p=pid: self._select_measurement(p))
                self.meas_list_layout.addWidget(card)
        self.meas_list_layout.addStretch()

    def _select_measurement(self, profile_id: int):
        self.selected_measurement_id = profile_id

    def _add_new_measurement(self):
        from app.ui.measurements.measurement_dialog import MeasurementDialog
        dlg = MeasurementDialog(
            customer_id=self.selected_customer.id if self.selected_customer else None,
            customer_name=self.selected_customer.name if self.selected_customer else "",
            parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted and dlg.result_data:
            try:
                data = dlg.result_data
                values = data.pop("values", {})
                profile = self.measurement_service.create_profile(**data, values=values)
                self.selected_measurement_id = profile.id
                self._refresh_measurement_list()
            except Exception as e:
                from app.utils.logger import get_logger
                get_logger(__name__).error(f"Create measurement error: {e}")

    # ─── Step 4: Order Details ───
    def _create_step4_details(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        title = QLabel("Order Details")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; color: {COLORS['primary']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.qty_input = QLineEdit("1")
        self.qty_input.setFixedHeight(42)
        form.addRow("Quantity:", self.qty_input)

        self.price_input = QLineEdit("0")
        self.price_input.setFixedHeight(42)
        self.price_input.setPlaceholderText("Price per item")
        form.addRow("Price:", self.price_input)

        self.order_date_input = QDateEdit()
        self.order_date_input.setDate(QDate.currentDate())
        self.order_date_input.setCalendarPopup(True)
        self.order_date_input.setFixedHeight(42)
        form.addRow("Order Date:", self.order_date_input)

        self.delivery_date_input = QDateEdit()
        self.delivery_date_input.setDate(QDate.currentDate().addDays(7))
        self.delivery_date_input.setCalendarPopup(True)
        self.delivery_date_input.setFixedHeight(42)
        form.addRow("Delivery Date:", self.delivery_date_input)

        self.instructions_input = QTextEdit()
        self.instructions_input.setMaximumHeight(80)
        self.instructions_input.setPlaceholderText("Any special instructions...")
        form.addRow("Instructions:", self.instructions_input)

        layout.addLayout(form)
        layout.addStretch()

        self.step4_error = QLabel()
        self.step4_error.setProperty("cssClass", "error")
        self.step4_error.setVisible(False)
        layout.addWidget(self.step4_error)

        footer = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setProperty("cssClass", "text")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self._go_to_step(2))
        footer.addWidget(back_btn)
        footer.addStretch()
        next_btn = QPushButton("Continue to Payment →")
        next_btn.setProperty("cssClass", "primary")
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.setFixedHeight(44)
        next_btn.clicked.connect(self._validate_step4)
        footer.addWidget(next_btn)
        layout.addLayout(footer)
        return page

    def _validate_step4(self):
        qty, err = validate_positive_int(self.qty_input.text(), "Quantity")
        if err:
            self.step4_error.setText(err)
            self.step4_error.setVisible(True)
            return
        price, err = validate_amount(self.price_input.text(), "Price", allow_zero=True)
        if err:
            self.step4_error.setText(err)
            self.step4_error.setVisible(True)
            return
        self.step4_error.setVisible(False)
        self._update_payment_summary()
        self._go_to_step(4)

    # ─── Step 5: Payment ───
    def _create_step5_payment(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        title = QLabel("Payment")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; color: {COLORS['primary']};")
        layout.addWidget(title)

        self.total_display = QLabel("Total: ₹0")
        self.total_display.setStyleSheet(f"font-size: 20px; font-weight: 600;")
        layout.addWidget(self.total_display)

        form = QFormLayout()
        form.setSpacing(12)

        self.advance_input = QLineEdit("0")
        self.advance_input.setFixedHeight(42)
        self.advance_input.setPlaceholderText("Advance payment amount")
        self.advance_input.textChanged.connect(self._update_remaining_display)
        form.addRow("Advance:", self.advance_input)

        self.method_combo = QComboBox()
        self.method_combo.addItems(PAYMENT_METHODS)
        self.method_combo.setFixedHeight(42)
        form.addRow("Payment Method:", self.method_combo)

        layout.addLayout(form)

        self.remaining_display = QLabel("Remaining: ₹0")
        self.remaining_display.setStyleSheet(f"font-size: 16px; color: {COLORS['on_surface_variant']};")
        layout.addWidget(self.remaining_display)

        self.step5_error = QLabel()
        self.step5_error.setProperty("cssClass", "error")
        self.step5_error.setVisible(False)
        layout.addWidget(self.step5_error)

        layout.addStretch()

        footer = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setProperty("cssClass", "text")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self._go_to_step(3))
        footer.addWidget(back_btn)
        footer.addStretch()
        next_btn = QPushButton("Review & Create Order →")
        next_btn.setProperty("cssClass", "primary")
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.setFixedHeight(44)
        next_btn.clicked.connect(self._validate_step5)
        footer.addWidget(next_btn)
        layout.addLayout(footer)
        return page

    def _update_payment_summary(self):
        try:
            qty = int(self.qty_input.text() or "0")
            price = float(self.price_input.text() or "0")
            total = qty * price
            self.total_display.setText(f"Total: {format_currency(total)}")
        except (ValueError, TypeError):
            self.total_display.setText("Total: ₹0")

    def _update_remaining_display(self):
        try:
            qty = int(self.qty_input.text() or "0")
            price = float(self.price_input.text() or "0")
            total = qty * price
            advance = float(self.advance_input.text() or "0")
            remaining = max(0, total - advance)
            self.remaining_display.setText(f"Remaining: {format_currency(remaining)}")
        except (ValueError, TypeError):
            self.remaining_display.setText("Remaining: ₹0")

    def _validate_step5(self):
        try:
            qty = int(self.qty_input.text() or "0")
            price = float(self.price_input.text() or "0")
            total = qty * price
            advance, err = validate_amount(self.advance_input.text(), "Advance", allow_zero=True)
            if err:
                self.step5_error.setText(err)
                self.step5_error.setVisible(True)
                return
            err = validate_advance(advance, total)
            if err:
                self.step5_error.setText(err)
                self.step5_error.setVisible(True)
                return
        except (ValueError, TypeError) as e:
            self.step5_error.setText(str(e))
            self.step5_error.setVisible(True)
            return
        self.step5_error.setVisible(False)
        self._build_confirmation()
        self._go_to_step(5)

    # ─── Step 6: Confirmation / Success ───
    def _create_step6_confirm(self) -> QWidget:
        page = QWidget()
        self.confirm_layout = QVBoxLayout(page)
        self.confirm_layout.setSpacing(16)
        return page

    def _build_confirmation(self):
        # Clear
        while self.confirm_layout.count():
            child = self.confirm_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub = child.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        title = QLabel("Review Order")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; color: {COLORS['primary']};")
        self.confirm_layout.addWidget(title)

        qty = int(self.qty_input.text() or "0")
        price = float(self.price_input.text() or "0")
        total = qty * price
        advance = float(self.advance_input.text() or "0")
        remaining = total - advance

        summary_text = (
            f"Customer: {self.selected_customer.name if self.selected_customer else '—'}\n"
            f"Clothing: {self.selected_clothing or '—'}\n"
            f"Quantity: {qty}\n"
            f"Price: {format_currency(price)}\n"
            f"Total: {format_currency(total)}\n"
            f"Advance: {format_currency(advance)}\n"
            f"Remaining: {format_currency(remaining)}\n"
            f"Order Date: {self.order_date_input.date().toString('dd/MM/yyyy')}\n"
            f"Delivery Date: {self.delivery_date_input.date().toString('dd/MM/yyyy')}\n"
            f"Payment Method: {self.method_combo.currentText()}"
        )

        summary = QLabel(summary_text)
        summary.setStyleSheet(f"""
            background-color: {COLORS['surface_container_lowest']};
            border: 1px solid {COLORS['surface_container_low']};
            border-radius: {CARD_RADIUS}px;
            padding: 20px;
            font-size: {FONT_SIZES['body_md']}px;
            line-height: 28px;
        """)
        self.confirm_layout.addWidget(summary)

        self.confirm_layout.addStretch()

        footer = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setProperty("cssClass", "text")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self._go_to_step(4))
        footer.addWidget(back_btn)
        footer.addStretch()

        create_btn = QPushButton("✅ Create Order")
        create_btn.setProperty("cssClass", "primary")
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.setFixedHeight(48)
        create_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 18px; font-weight: 600;
                padding: 0 32px;
                background-color: {COLORS['primary']};
                color: {COLORS['on_primary']};
                border: none; border-radius: 12px;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_container']}; }}
        """)
        create_btn.clicked.connect(self._create_order)
        footer.addWidget(create_btn)
        self.confirm_layout.addLayout(footer)

    def _create_order(self):
        try:
            qty = int(self.qty_input.text())
            price = float(self.price_input.text())
            advance = float(self.advance_input.text() or "0")
            order_date_q = self.order_date_input.date()
            delivery_date_q = self.delivery_date_input.date()

            order_date = date(order_date_q.year(), order_date_q.month(), order_date_q.day())
            delivery_date = date(delivery_date_q.year(), delivery_date_q.month(), delivery_date_q.day())

            order = self.order_service.create_order(
                customer_id=self.selected_customer.id,
                clothing_type=self.selected_clothing,
                measurement_profile_id=self.selected_measurement_id,
                quantity=qty,
                price=price,
                order_date=order_date,
                delivery_date=delivery_date,
                special_instructions=self.instructions_input.toPlainText().strip(),
                advance_amount=advance,
                payment_method=self.method_combo.currentText(),
            )
            self.created_order = order
            self._show_success(order)

        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Order creation error: {e}")
            from app.ui.widgets.dialogs import MessageDialog
            MessageDialog("Error", f"Unable to create order. Please try again.\n\n{e}", "❌", self).exec()

    def _show_success(self, order):
        while self.confirm_layout.count():
            child = self.confirm_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub = child.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        self.confirm_layout.addStretch()

        icon = QLabel("✅")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.confirm_layout.addWidget(icon)

        success_title = QLabel("Order Created Successfully!")
        success_title.setStyleSheet(f"font-size: 24px; font-weight: 600; color: {COLORS['status_ready']};")
        success_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.confirm_layout.addWidget(success_title)

        info = QLabel(
            f"Order Number: {order.order_number}\n"
            f"Customer: {self.selected_customer.name}\n"
            f"Delivery Date: {format_date_display(order.delivery_date)}\n"
            f"Total: {format_currency(order.total_amount)}\n"
            f"Advance: {format_currency(order.advance_amount)}\n"
            f"Remaining: {format_currency(order.remaining_amount)}\n"
            f"Status: {order.status}"
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet(f"""
            background-color: {COLORS['surface_container_lowest']};
            border: 1px solid {COLORS['surface_container_low']};
            border-radius: {CARD_RADIUS}px;
            padding: 24px;
            font-size: 15px;
            line-height: 28px;
        """)
        self.confirm_layout.addWidget(info)

        self.confirm_layout.addSpacing(16)

        btns = QHBoxLayout()
        btns.setSpacing(12)
        btns.addStretch()

        receipt_btn = QPushButton("🖨️ Print Receipt")
        receipt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        receipt_btn.setFixedHeight(40)
        receipt_btn.clicked.connect(lambda: self.print_receipt_requested.emit(order.id))
        btns.addWidget(receipt_btn)

        slip_btn = QPushButton("📋 Print Stitching Slip")
        slip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        slip_btn.setFixedHeight(40)
        slip_btn.clicked.connect(lambda: self.print_slip_requested.emit(order.id))
        btns.addWidget(slip_btn)

        view_btn = QPushButton("👁️ View Order")
        view_btn.setProperty("cssClass", "primary")
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setFixedHeight(40)
        view_btn.clicked.connect(lambda: self.view_order_requested.emit(order.id))
        btns.addWidget(view_btn)

        btns.addStretch()
        self.confirm_layout.addLayout(btns)
        self.confirm_layout.addStretch()

        self.order_created.emit(order)

    # ─── Navigation ───
    def _go_to_step(self, step: int):
        if step == 2:
            self._refresh_measurement_list()
        self.current_step = step
        self.stack.setCurrentIndex(step)
        self._update_progress()

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_customer_list()
