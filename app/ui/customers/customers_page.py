from __future__ import annotations
"""Customers page — list, search, and manage customers."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QLineEdit, QTableWidget,
                                QTableWidgetItem, QHeaderView, QAbstractItemView,
                                QScrollArea)
from PySide6.QtCore import Signal, Qt

from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG, STACK_MD
from app.services.customer_service import CustomerService
from app.utils.formatters import format_date_display


class CustomersPage(QWidget):
    """Customers list page with search and CRUD."""

    add_customer_requested = Signal()
    view_customer_requested = Signal(int)  # customer_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.customer_service = CustomerService()
        self.current_page = 1
        self.page_size = 50
        self.total_count = 0
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(CONTAINER_PADDING, CONTAINER_PADDING,
                                   CONTAINER_PADDING, CONTAINER_PADDING)
        layout.setSpacing(STACK_LG)

        # Header
        header = QHBoxLayout()
        title = QLabel("Customers")
        title.setStyleSheet(f"""
            font-size: 32px; font-weight: 600;
            color: {COLORS['on_surface']};
        """)
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("  ＋  Add Customer")
        add_btn.setProperty("cssClass", "primary")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self.add_customer_requested.emit)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Search
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search by name, mobile, or customer ID...")
        self.search_input.setFixedHeight(44)
        self.search_input.textChanged.connect(self._on_search)
        search_row.addWidget(self.search_input)

        self.count_label = QLabel("0 customers")
        self.count_label.setStyleSheet(f"""
            font-size: {FONT_SIZES['label_sm']}px;
            color: {COLORS['on_surface_variant']};
            padding: 0 8px;
        """)
        search_row.addWidget(self.count_label)
        layout.addLayout(search_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Mobile", "Address", "Created", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(5, 80)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(400)
        self.table.doubleClicked.connect(self._on_row_double_click)
        layout.addWidget(self.table)

        # Empty state
        self.empty_label = QLabel("No customers found\nAdd your first customer to get started!")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"""
            font-size: {FONT_SIZES['body_lg']}px;
            color: {COLORS['on_surface_variant']};
            padding: 60px;
        """)
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)

        # Pagination Controls
        pagination_row = QHBoxLayout()
        pagination_row.addStretch()
        
        self.btn_prev = QPushButton("◄ Previous")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.clicked.connect(self._prev_page)
        
        self.lbl_page = QLabel("Page 1")
        self.lbl_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_page.setFixedWidth(100)
        
        self.btn_next = QPushButton("Next ►")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.clicked.connect(self._next_page)
        
        pagination_row.addWidget(self.btn_prev)
        pagination_row.addWidget(self.lbl_page)
        pagination_row.addWidget(self.btn_next)
        pagination_row.addStretch()
        
        layout.addLayout(pagination_row)

        layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh_data(self):
        try:
            offset = (self.current_page - 1) * self.page_size
            text = self.search_input.text().strip()
            
            if text:
                customers, total = self.customer_service.search_customers(text, limit=self.page_size, offset=offset)
            else:
                customers, total = self.customer_service.get_all_customers(limit=self.page_size, offset=offset)
                
            self.total_count = total
            self._update_pagination_ui()
            self._populate_table(customers)
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Error loading customers: {e}")

    def _on_search(self, text: str):
        self.current_page = 1
        self.refresh_data()
        
    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_data()
            
    def _next_page(self):
        max_page = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        if self.current_page < max_page:
            self.current_page += 1
            self.refresh_data()
            
    def _update_pagination_ui(self):
        max_page = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        self.lbl_page.setText(f"Page {self.current_page} of {max_page}")
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < max_page)
        self.count_label.setText(f"{self.total_count} customer{'s' if self.total_count != 1 else ''}")

    def _populate_table(self, customers: list):
        self.table.setRowCount(len(customers))
        self.empty_label.setVisible(len(customers) == 0)
        self.table.setVisible(len(customers) > 0)

        for row, c in enumerate(customers):
            self.table.setItem(row, 0, QTableWidgetItem(str(c.id)))
            self.table.setItem(row, 1, QTableWidgetItem(c.name))
            self.table.setItem(row, 2, QTableWidgetItem(c.mobile or "—"))
            self.table.setItem(row, 3, QTableWidgetItem(c.address or "—"))
            self.table.setItem(row, 4, QTableWidgetItem(
                format_date_display(c.created_at) if c.created_at else "—"))

            view_btn = QPushButton("View")
            view_btn.setProperty("cssClass", "text")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.setFixedHeight(32)
            cid = c.id
            view_btn.clicked.connect(lambda checked, i=cid: self.view_customer_requested.emit(i))
            action_w = QWidget()
            al = QHBoxLayout(action_w)
            al.setContentsMargins(4, 4, 4, 4)
            al.addWidget(view_btn)
            self.table.setCellWidget(row, 5, action_w)

        self.table.resizeRowsToContents()

    def _on_row_double_click(self, index):
        row = index.row()
        id_item = self.table.item(row, 0)
        if id_item:
            self.view_customer_requested.emit(int(id_item.text()))
