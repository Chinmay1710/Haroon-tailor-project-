from __future__ import annotations
"""Main window — the root application window embedding QWebEngineView for an exact UI match."""

import os
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtWebChannel import QWebChannel

from app.database.engine import get_session, init_db
from app.repositories.settings_repo import SettingsRepository
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.measurement_service import MeasurementService
from app.services.expense_service import ExpenseService
from app.services.report_service import ReportService
from app.services.backup_service import BackupService
from app.services.worker_service import worker_service
from app.services.stock_service import StockService
from app.utils.logger import get_logger
from app.ui.web_bridge import WebBridge

logger = get_logger(__name__)

class CustomWebPage(QWebEnginePage):
    """Custom web page to handle javascript dialogs like alert() and confirm()."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.featurePermissionRequested.connect(self._handle_feature_permission)
        
    def _handle_feature_permission(self, securityOrigin, feature):
        if feature in (QWebEnginePage.Feature.MediaAudioCapture, QWebEnginePage.Feature.MediaVideoCapture, QWebEnginePage.Feature.MediaAudioVideoCapture):
            self.setFeaturePermission(securityOrigin, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)
        else:
            self.setFeaturePermission(securityOrigin, feature, QWebEnginePage.PermissionPolicy.PermissionDeniedByUser)

    def javaScriptAlert(self, securityOrigin, msg):
        QMessageBox.information(None, "Message", msg)

    def javaScriptConfirm(self, securityOrigin, msg):
        reply = QMessageBox.question(None, "Confirmation", msg,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes

class MainWindow(QMainWindow):
    """Root application window rendering HTML via WebEngine."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tailor Shop Manager")
        self.setMinimumSize(QSize(1200, 800))
        self.resize(1400, 900)

        # Initialize database
        init_db()

        # Initialize Services
        self.services = {
            'customer': CustomerService(),
            'order': OrderService(),
            'payment': PaymentService(),
            'measurement': MeasurementService(),
            'expense': ExpenseService(),
            'report': ReportService(),
            'backup': BackupService(),
            'worker': worker_service,
            'stock': StockService()
        }

        self._build_web_ui()

    def _build_web_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView()
        self.web_view.setPage(CustomWebPage(self.web_view))
        
        # Allow Chromium to cache CSS/JS/fonts across sessions for faster page loads
        # (previously clearHttpCache() was called here, causing slow startup)
        
        layout.addWidget(self.web_view)
        
        self.setCentralWidget(central)

        # Setup QWebChannel for JS-Python communication
        self.channel = QWebChannel()
        self.bridge = WebBridge(self.services, parent=self)
        self.bridge.navigate_requested.connect(self._navigate_to)
        self.bridge.dictation_result_requested.connect(self._handle_dictation_result)
        
        # Register the bridge object to be accessible as `bridge` in javascript
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        self.web_view.page().printRequested.connect(self._handle_print_requested)

        # Check setup and navigate
        session = get_session()
        try:
            repo = SettingsRepository(session)
            if not repo.is_setup_done():
                # We don't have a setup HTML in the reference, but we can fallback or just go to dashboard
                self._navigate_to("dashboard")
            else:
                self._navigate_to("dashboard")
        finally:
            session.close()

    def _navigate_to(self, page_name: str):
        """Navigate the web view to the corresponding HTML file."""
        from app.config import ASSETS_DIR
        html_file = f"{page_name}.html"
        base_dir = os.path.join(ASSETS_DIR, 'www', 'html')
        file_path = os.path.join(base_dir, html_file)
        
        if os.path.exists(file_path):
            url = QUrl.fromLocalFile(file_path)
            self.web_view.setUrl(url)
            logger.info(f"Navigating to {file_path}")
        else:
            logger.error(f"Page {page_name} not found at {file_path}")

    def _handle_dictation_result(self, textarea_id: str, text: str, error: str):
        """Sends the transcription result to the Javascript frontend."""
        # Escape strings for safe JS injection
        import json
        text_json = json.dumps(text)
        error_json = json.dumps(error)
        script = f"if (window.API && window.API.handleDictationResult) {{ window.API.handleDictationResult('{textarea_id}', {text_json}, {error_json}); }}"
        self.web_view.page().runJavaScript(script)

    def _handle_print_requested(self):
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.web_view.page().print(printer, lambda success: logger.info(f"Print finished: success={success}"))

    # ─── Close Event ───
    def closeEvent(self, event):
        """Optionally create backup on close."""
        try:
            session = get_session()
            try:
                settings = SettingsRepository(session).get_settings()
                if settings.auto_backup:
                    BackupService().create_backup()
                    logger.info("Auto-backup created on exit")
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Auto-backup failed: {e}")

        from app.database.engine import close_db
        close_db()
        event.accept()
