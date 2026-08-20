from __future__ import annotations
"""Expenses page — list, add, edit expenses."""

from datetime import date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QLineEdit, QTableWidget,
                                QTableWidgetItem, QHeaderView, QAbstractItemView,
                                QScrollArea, QDialog, QFormLayout, QComboBox,
                                QDateEdit, QTextEdit)
from PySide6.QtCore import Signal, Qt, QDate
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG
from app.config import EXPENSE_CATEGORIES
from app.services.expense_service import ExpenseService
from app.utils.formatters import format_currency, format_date_display
from app.utils.validators import validate_required, validate_amount


class ExpenseDialog(QDialog):
    def __init__(self, expense=None, parent=None):
        super().__init__(parent)
        self.expense = expense
        self.result_data = None
        self.setWindowTitle("Edit Expense" if expense else "Add Expense")
        self.setFixedWidth(460)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['surface_container_lowest']}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Edit Expense" if self.expense else "Add Expense")
        title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600; color: {COLORS['primary']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Expense name")
        self.name_input.setFixedHeight(42)
        form.addRow("Name *:", self.name_input)

        self.category_combo = QComboBox()
        self.category_combo.addItems(EXPENSE_CATEGORIES)
        self.category_combo.setFixedHeight(42)
        form.addRow("Category:", self.category_combo)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.amount_input.setFixedHeight(42)
        form.addRow("Amount *:", self.amount_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setFixedHeight(42)
        form.addRow("Date:", self.date_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(60)
        self.note_input.setPlaceholderText("Optional note")
        form.addRow("Note:", self.note_input)

        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setProperty("cssClass", "error")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        save_btn = QPushButton("Save Expense")
        save_btn.setProperty("cssClass", "primary")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        if self.expense:
            self.name_input.setText(self.expense.name)
            self.category_combo.setCurrentText(self.expense.category)
            self.amount_input.setText(str(self.expense.amount))
            if self.expense.expense_date:
                d = self.expense.expense_date
                self.date_input.setDate(QDate(d.year, d.month, d.day))
            self.note_input.setPlainText(self.expense.note or "")

    def _on_save(self):
        name = self.name_input.text().strip()
        err = validate_required("Name", name)
        if err:
            self.error_label.setText(err); self.error_label.setVisible(True); return
        amount, err = validate_amount(self.amount_input.text(), "Amount")
        if err:
            self.error_label.setText(err); self.error_label.setVisible(True); return
        qd = self.date_input.date()
        self.result_data = {
            "name": name,
            "category": self.category_combo.currentText(),
            "amount": amount,
            "expense_date": date(qd.year(), qd.month(), qd.day()),
            "note": self.note_input.toPlainText().strip(),
        }
        self.accept()


class ExpensesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expense_service = ExpenseService()
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

        header = QHBoxLayout()
        title = QLabel("Expenses")
        title.setStyleSheet(f"font-size: 32px; font-weight: 600; color: {COLORS['on_surface']};")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("  ＋  Add Expense")
        add_btn.setProperty("cssClass", "primary")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self._add_expense)
        header.addWidget(add_btn)
        layout.addLayout(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search expenses...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self._on_search)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Name", "Category", "Amount", "Note", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)

        self.empty_label = QLabel("No expenses found\nAdd your first expense!")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"font-size: {FONT_SIZES['body_lg']}px; color: {COLORS['on_surface_variant']}; padding: 60px;")
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)
        layout.addStretch()
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh_data(self):
        try:
            from app.database.engine import get_session
            from app.repositories.settings_repo import SettingsRepository
            session = get_session()
            try:
                currency = SettingsRepository(session).get_settings().currency or "₹"
            finally:
                session.close()

            query = self.search_input.text().strip()
            expenses = self.expense_service.search_expenses(query) if query else self.expense_service.get_all_expenses()
            self._populate(expenses, currency)
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Error loading expenses: {e}")

    def _on_search(self, text):
        self.refresh_data()

    def _populate(self, expenses, currency):
        self.table.setRowCount(len(expenses))
        self.empty_label.setVisible(len(expenses) == 0)
        self.table.setVisible(len(expenses) > 0)
        for row, e in enumerate(expenses):
            self.table.setItem(row, 0, QTableWidgetItem(format_date_display(e.expense_date)))
            self.table.setItem(row, 1, QTableWidgetItem(e.name))
            self.table.setItem(row, 2, QTableWidgetItem(e.category))
            self.table.setItem(row, 3, QTableWidgetItem(format_currency(e.amount, currency)))
            self.table.setItem(row, 4, QTableWidgetItem(e.note or "—"))

            actions = QWidget()
            al = QHBoxLayout(actions)
            al.setContentsMargins(4, 4, 4, 4)
            edit_btn = QPushButton("Edit")
            edit_btn.setProperty("cssClass", "text")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            eid = e.id
            edit_btn.clicked.connect(lambda checked, i=eid: self._edit_expense(i))
            al.addWidget(edit_btn)
            del_btn = QPushButton("🗑️")
            del_btn.setProperty("cssClass", "text")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda checked, i=eid: self._delete_expense(i))
            al.addWidget(del_btn)
            self.table.setCellWidget(row, 5, actions)
        self.table.resizeRowsToContents()

    def _add_expense(self):
        dlg = ExpenseDialog(parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted and dlg.result_data:
            try:
                self.expense_service.create_expense(**dlg.result_data)
                self.refresh_data()
            except Exception as e:
                from app.utils.logger import get_logger
                get_logger(__name__).error(f"Add expense error: {e}")

    def _edit_expense(self, expense_id: int):
        from app.database.engine import get_session
        from app.repositories.expense_repo import ExpenseRepository
        session = get_session()
        try:
            expense = ExpenseRepository(session).get_by_id(expense_id)
        finally:
            session.close()
        if expense:
            dlg = ExpenseDialog(expense=expense, parent=self)
            if dlg.exec() == dlg.DialogCode.Accepted and dlg.result_data:
                try:
                    self.expense_service.update_expense(expense_id, **dlg.result_data)
                    self.refresh_data()
                except Exception as e:
                    from app.utils.logger import get_logger
                    get_logger(__name__).error(f"Edit expense error: {e}")

    def _delete_expense(self, expense_id: int):
        from app.ui.widgets.dialogs import ConfirmDialog
        dlg = ConfirmDialog("Delete Expense", "Are you sure?", "Delete", danger=True, parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            try:
                self.expense_service.delete_expense(expense_id)
                self.refresh_data()
            except Exception as e:
                from app.utils.logger import get_logger
                get_logger(__name__).error(f"Delete expense error: {e}")
