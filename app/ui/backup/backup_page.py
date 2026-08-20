from __future__ import annotations
"""Backup & Restore page."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QFileDialog, QTableWidget,
                                QTableWidgetItem, QHeaderView, QAbstractItemView,
                                QScrollArea)
from PySide6.QtCore import Signal, Qt
from app.ui.theme import COLORS, FONT_SIZES, CONTAINER_PADDING, STACK_LG, CARD_RADIUS
from app.ui.widgets.dialogs import ConfirmDialog, MessageDialog
from app.ui.widgets.notification import show_toast
from app.services.backup_service import BackupService
from app.utils.formatters import format_date_display


class BackupPage(QWidget):
    """Backup & Restore page."""
    restart_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.backup_service = BackupService()
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

        title = QLabel("Backup & Restore")
        title.setStyleSheet(f"font-size: 32px; font-weight: 600; color: {COLORS['on_surface']};")
        layout.addWidget(title)

        # Last backup info
        self.last_backup_label = QLabel("Last backup: Never")
        self.last_backup_label.setStyleSheet(f"""
            font-size: {FONT_SIZES['body_md']}px;
            color: {COLORS['on_surface_variant']};
            padding: 16px;
            background-color: {COLORS['surface_container_lowest']};
            border: 1px solid {COLORS['surface_container_low']};
            border-radius: {CARD_RADIUS}px;
        """)
        layout.addWidget(self.last_backup_label)

        # Buttons
        btns = QHBoxLayout()
        btns.setSpacing(16)

        backup_btn = QPushButton("💾 Create Backup")
        backup_btn.setProperty("cssClass", "primary")
        backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_btn.setFixedHeight(48)
        backup_btn.setMinimumWidth(200)
        backup_btn.clicked.connect(self._create_backup)
        btns.addWidget(backup_btn)

        restore_btn = QPushButton("📂 Restore from Backup")
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.setFixedHeight(48)
        restore_btn.setMinimumWidth(200)
        restore_btn.clicked.connect(self._restore_backup)
        btns.addWidget(restore_btn)

        btns.addStretch()
        layout.addLayout(btns)

        # Backup history
        history_title = QLabel("📋 Backup History")
        history_title.setStyleSheet(f"font-size: {FONT_SIZES['headline_md']}px; font-weight: 600;")
        layout.addWidget(history_title)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "File", "Size", "Status"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setShowGrid(False)
        self.history_table.setMinimumHeight(200)
        layout.addWidget(self.history_table)

        layout.addStretch()
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh_data(self):
        try:
            last = self.backup_service.get_last_backup_date()
            if last:
                self.last_backup_label.setText(f"Last backup: {format_date_display(last)}")
            else:
                self.last_backup_label.setText("Last backup: Never — We recommend backing up regularly!")

            logs = self.backup_service.get_backup_history()
            self.history_table.setRowCount(len(logs))
            for row, log in enumerate(logs):
                self.history_table.setItem(row, 0, QTableWidgetItem(
                    format_date_display(log.backup_date)))
                import os
                self.history_table.setItem(row, 1, QTableWidgetItem(
                    os.path.basename(log.backup_path)))
                size = f"{log.file_size / 1024:.1f} KB" if log.file_size else "—"
                self.history_table.setItem(row, 2, QTableWidgetItem(size))
                self.history_table.setItem(row, 3, QTableWidgetItem(log.status))
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger(__name__).error(f"Backup page error: {e}")

    def _create_backup(self):
        try:
            folder = QFileDialog.getExistingDirectory(
                self, "Select Backup Folder",
                self.backup_service.get_backup_location())
            if folder:
                path = self.backup_service.create_backup(folder)
                show_toast(self, f"Backup created successfully!\n{path}", "success", 5000)
                self.refresh_data()
        except Exception as e:
            show_toast(self, f"Backup failed: {e}", "error")

    def _restore_backup(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "",
            "Database Files (*.db);;All Files (*)")
        if not path:
            return

        dlg = ConfirmDialog(
            "Restore Backup",
            "This will replace your current data with the backup.\n"
            "All changes since the backup will be lost.\n\n"
            "Are you sure you want to continue?",
            "Restore", danger=True, parent=self)

        if dlg.exec() == dlg.DialogCode.Accepted:
            try:
                self.backup_service.restore_backup(path)
                MessageDialog(
                    "Restore Complete",
                    "Database restored successfully.\nPlease restart the application.",
                    "✅", self).exec()
            except Exception as e:
                show_toast(self, f"Restore failed: {e}", "error")

