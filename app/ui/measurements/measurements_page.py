from __future__ import annotations
"""Measurements page — list and manage measurement profiles."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QHeaderView, QAbstractItemView, QScrollArea)
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG, STACK_MD
from app.services.measurement_service import MeasurementService
from app.utils.formatters import format_date_display


class MeasurementsPage(QWidget):
    """Measurements list page."""

    add_measurement_requested = Signal()
    edit_measurement_requested = Signal(int)
    view_customer_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.measurement_service = MeasurementService()
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(CONTAINER_PADDING, CONTAINER_PADDING,
                                   CONTAINER_PADDING, CONTAINER_PADDING)
        layout.setSpacing(STACK_LG)

        # Header
        header = QHBoxLayout()
        title = QLabel("Measurements")
        title.setStyleSheet(f"font-size: 32px; font-weight: 600; color: {COLORS['on_surface']};")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("  ＋  Add Measurement")
        add_btn.setProperty("cssClass", "primary")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self.add_measurement_requested.emit)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Template", "Name", "Unit", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)

        self.empty_label = QLabel("No measurements found\nAdd your first measurement profile!")
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
            profiles = self.measurement_service.get_all_profiles()
            self.table.setRowCount(len(profiles))
            self.empty_label.setVisible(len(profiles) == 0)
            self.table.setVisible(len(profiles) > 0)

            for row, p in enumerate(profiles):
                self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
                cust_name = p.customer.name if p.customer else "—"
                self.table.setItem(row, 1, QTableWidgetItem(cust_name))
                self.table.setItem(row, 2, QTableWidgetItem(p.template_type))
                self.table.setItem(row, 3, QTableWidgetItem(p.name))
                self.table.setItem(row, 4, QTableWidgetItem(p.unit))

                actions = QWidget()
                al = QHBoxLayout(actions)
                al.setContentsMargins(4, 4, 4, 4)
                al.setSpacing(4)

                edit_btn = QPushButton("Edit")
                edit_btn.setProperty("cssClass", "text")
                edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                pid = p.id
                edit_btn.clicked.connect(lambda checked, i=pid: self.edit_measurement_requested.emit(i))
                al.addWidget(edit_btn)

                dup_btn = QPushButton("Copy")
                dup_btn.setProperty("cssClass", "text")
                dup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                dup_btn.clicked.connect(lambda checked, i=pid: self._duplicate(i))
                al.addWidget(dup_btn)

                del_btn = QPushButton("🗑️")
                del_btn.setProperty("cssClass", "text")
                del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                del_btn.clicked.connect(lambda checked, i=pid: self._delete(i))
                al.addWidget(del_btn)

                self.table.setCellWidget(row, 5, actions)
            self.table.resizeRowsToContents()
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Error loading measurements: {e}")

    def _duplicate(self, profile_id: int):
        try:
            self.measurement_service.duplicate_profile(profile_id)
            self.refresh_data()
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Duplicate error: {e}")

    def _delete(self, profile_id: int):
        from app.ui.widgets.dialogs import ConfirmDialog
        dlg = ConfirmDialog("Delete Measurement",
                            "Are you sure you want to delete this measurement profile?",
                            "Delete", danger=True, parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            try:
                self.measurement_service.delete_profile(profile_id)
                self.refresh_data()
            except Exception as e:
                from app.utils.logger import get_logger
                get_logger(__name__).error(f"Delete error: {e}")
