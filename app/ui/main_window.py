from __future__ import annotations

"""Main window — the root application window embedding QWebEngineView for an exact UI match."""

import os
import re
import json

from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

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
    """Custom web page to handle JavaScript dialogs and permissions."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.featurePermissionRequested.connect(
            self._handle_feature_permission
        )

    def _handle_feature_permission(
        self,
        securityOrigin,
        feature,
    ):
        """Handle browser feature permissions."""

        if feature in (
            QWebEnginePage.Feature.MediaAudioCapture,
            QWebEnginePage.Feature.MediaVideoCapture,
            QWebEnginePage.Feature.MediaAudioVideoCapture,
        ):
            self.setFeaturePermission(
                securityOrigin,
                feature,
                QWebEnginePage.PermissionPolicy.PermissionGrantedByUser,
            )
        else:
            self.setFeaturePermission(
                securityOrigin,
                feature,
                QWebEnginePage.PermissionPolicy.PermissionDeniedByUser,
            )

    def javaScriptAlert(
        self,
        securityOrigin,
        msg,
    ):
        """Handle JavaScript alert()."""

        QMessageBox.information(
            None,
            "Message",
            msg,
        )

    def javaScriptConfirm(
        self,
        securityOrigin,
        msg,
    ):
        """Handle JavaScript confirm()."""

        reply = QMessageBox.question(
            None,
            "Confirmation",
            msg,
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        return reply == QMessageBox.StandardButton.Yes


class MainWindow(QMainWindow):
    """Root application window rendering HTML via WebEngine."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Tailor Shop Manager"
        )

        self.setMinimumSize(
            QSize(1200, 800)
        )

        self.resize(
            1400,
            900,
        )

        # ---------------------------------------------------------------
        # Initialize database
        # ---------------------------------------------------------------

        init_db()

        # Start Worker Portal Server and Tunnel
        try:
            from app.web.server import WebServerThread
            from app.web.tunnel import NgrokTunnel
            self.worker_server = WebServerThread(port=8000)
            self.worker_server.start()
            
            self.tunnel = NgrokTunnel(port=8000)
            self.tunnel_url = self.tunnel.start()
            logger.info(f"Worker portal started at {self.tunnel_url}")
        except Exception as e:
            logger.error(f"Failed to start worker portal: {e}")
            self.tunnel_url = None

        # ---------------------------------------------------------------
        # Initialize services
        # ---------------------------------------------------------------
        self.services = {
            "customer": CustomerService(),
            "order": OrderService(),
            "payment": PaymentService(),
            "measurement": MeasurementService(),
            "expense": ExpenseService(),
            "report": ReportService(),
            "backup": BackupService(),
            "worker": worker_service,
            "stock": StockService(),
        }

        self._build_web_ui()

    def _build_web_ui(self):
        """Build the WebEngine-based application UI."""

        central = QWidget()

        layout = QVBoxLayout(
            central
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        # ---------------------------------------------------------------
        # Web view
        # ---------------------------------------------------------------

        self.web_view = QWebEngineView()

        self.web_view.setPage(
            CustomWebPage(
                self.web_view
            )
        )

        # Allow Chromium to cache CSS/JS/fonts across sessions
        # for faster page loads.
        layout.addWidget(
            self.web_view
        )

        self.setCentralWidget(
            central
        )

        # ---------------------------------------------------------------
        # QWebChannel
        # ---------------------------------------------------------------

        self.channel = QWebChannel()

        self.bridge = WebBridge(
            self.services,
            parent=self,
        )

        self.bridge.navigate_requested.connect(
            self._navigate_to
        )

        self.bridge.dictation_result_requested.connect(
            self._handle_dictation_result
        )
        
        self.bridge.customer_added.connect(
            self._on_customer_added
        )

        self.bridge.order_added.connect(
            self._on_order_added
        )

        # Register bridge instance in the web server so API requests can emit signals
        try:
            import app.web.server
            app.web.server.bridge_instance = self.bridge
        except Exception as e:
            logger.error(f"Failed to register bridge in server: {e}")

        self.bridge.save_pdf_requested.connect(
            self._handle_save_pdf
        )

        # Register bridge object for JavaScript.
        self.channel.registerObject(
            "bridge",
            self.bridge,
        )

        self.web_view.page().setWebChannel(
            self.channel
        )

        # ---------------------------------------------------------------
        # Print request
        # ---------------------------------------------------------------
        #
        # The old implementation used:
        #
        # self.web_view.page().print(...)
        #
        # QWebEnginePage in this environment does not provide that
        # method, which caused:
        #
        # AttributeError:
        # 'CustomWebPage' object has no attribute 'print'
        #
        # We keep the existing printRequested signal, but handle it
        # using our application's receipt printer.
        # ---------------------------------------------------------------

        self.web_view.page().printRequested.connect(
            self._handle_print_requested
        )

        # ---------------------------------------------------------------
        # Initial navigation
        # ---------------------------------------------------------------

        session = get_session()

        try:
            repo = SettingsRepository(
                session
            )

            if not repo.is_setup_done():
                self._navigate_to(
                    "dashboard"
                )
            else:
                self._navigate_to(
                    "dashboard"
                )

        finally:
            session.close()

    def _navigate_to(
        self,
        page_name: str,
    ):
        """Navigate the web view to the corresponding HTML file."""

        from app.config import ASSETS_DIR

        html_file = (
            f"{page_name}.html"
        )

        base_dir = os.path.join(
            ASSETS_DIR,
            "www",
            "html",
        )

        file_path = os.path.join(
            base_dir,
            html_file,
        )

        if os.path.exists(
            file_path
        ):
            url = QUrl.fromLocalFile(
                file_path
            )

            self.web_view.setUrl(
                url
            )

            logger.info(
                f"Navigating to {file_path}"
            )

        else:
            logger.error(
                f"Page {page_name} not found "
                f"at {file_path}"
            )

    def _handle_dictation_result(
        self,
        textarea_id: str,
        text: str,
        error: str,
    ):
        """Send transcription result to the JavaScript frontend."""

        # Escape strings for safe JavaScript injection.
        text_json = json.dumps(
            text
        )

        error_json = json.dumps(
            error
        )

        script = (
            "if (window.API && "
            "window.API.handleDictationResult) { "
            f"window.API.handleDictationResult("
            f"'{textarea_id}', "
            f"{text_json}, "
            f"{error_json}"
            "); }"
        )

        self.web_view.page().runJavaScript(
            script
        )

    def _on_customer_added(self):
        """Trigger UI refresh when a customer is added via the QR code portal."""
        # This will call loadCustomers() if it exists on the page
        script = "if (typeof window.loadCustomers === 'function') { window.loadCustomers(); } else if (window.location.href.includes('customers')) { window.location.reload(); }"
        self.web_view.page().runJavaScript(script)

    def _on_order_added(self):
        """Trigger UI refresh when an order is added via the QR code portal."""
        script = """
        if (typeof window.loadOrders === 'function') { 
            window.loadOrders(); 
        } else if (typeof window.loadDashboard === 'function') { 
            window.loadDashboard(); 
        } else {
            window.location.reload();
        }
        """
        self.web_view.page().runJavaScript(script)

    def _handle_print_requested(self):
        """Handle the print request from the receipt preview.
        
        The user requested that the print EXACTLY matches the HTML preview.
        We will use printToPdf to generate a temporary PDF and then send it to the system printer.
        """
        try:
            logger.info("Print requested directly from HTML preview.")
            
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            from PySide6.QtCore import QByteArray
            
            # Ask user for printer
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                printer_name = printer.printerName()
                logger.info(f"Selected printer: {printer_name}")
                
                def pdf_generated_callback(pdf_data: QByteArray):
                    if pdf_data.isEmpty():
                        logger.error("Generated PDF data is empty.")
                        return
                    
                    import tempfile
                    import os
                    import platform
                    
                    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
                    with os.fdopen(fd, 'wb') as f:
                        f.write(pdf_data.data())
                    
                    logger.info(f"HTML printed to temporary PDF: {temp_path}")
                    
                    # Print the PDF using OS tools
                    try:
                        sys_platform = platform.system().lower()
                        if sys_platform == 'darwin':
                            # macOS
                            cmd = f'lpr -P "{printer_name}" "{temp_path}"'
                            os.system(cmd)
                        elif sys_platform == 'windows':
                            # Windows
                            os.startfile(temp_path, "print")
                        else:
                            # Linux
                            cmd = f'lp -d "{printer_name}" "{temp_path}"'
                            os.system(cmd)
                    except Exception as e:
                        logger.error(f"Failed to print PDF via OS: {e}")
                
                # Force 58mm POS receipt layout regardless of the printer's default
                from PySide6.QtGui import QPageLayout, QPageSize
                from PySide6.QtCore import QSizeF, QMarginsF
                from app.printing.receipt_printer import THERMAL_PAPER_WIDTH_MM, THERMAL_PAPER_HEIGHT_MM
                
                page_size = QPageSize(
                    QSizeF(THERMAL_PAPER_WIDTH_MM, THERMAL_PAPER_HEIGHT_MM),
                    QPageSize.Unit.Millimeter,
                    "POS58 Receipt"
                )
                page_layout = QPageLayout(page_size, QPageLayout.Orientation.Portrait, QMarginsF(0, 0, 0, 0))
                
                # Request the page to print itself to a PDF byte array using our forced 58mm layout
                self.web_view.page().printToPdf(pdf_generated_callback, page_layout)

        except Exception as e:
            logger.exception(f"Error handling print request: {e}")

    def _handle_save_pdf(self, pdf_type: str, output_path: str):
        """Handle save pdf request from web bridge using printToPdf."""
        try:
            logger.info(f"Save PDF requested: type={pdf_type}, path={output_path}")
            
            def pdf_generated_callback(pdf_data: QByteArray):
                if pdf_data.isEmpty():
                    logger.error("Generated PDF data is empty.")
                    return
                
                try:
                    with open(output_path, 'wb') as f:
                        f.write(pdf_data.data())
                    logger.info(f"PDF successfully saved to {output_path}")
                except Exception as e:
                    logger.error(f"Failed to write PDF file: {e}")
            
            from PySide6.QtGui import QPageLayout, QPageSize
            from PySide6.QtCore import QSizeF, QMarginsF
            from app.printing.receipt_printer import THERMAL_PAPER_WIDTH_MM, THERMAL_PAPER_HEIGHT_MM
            
            # Use 58mm POS receipt layout for both receipt and stitching slip
            # as requested by the user to match structures.
            page_size = QPageSize(
                QSizeF(THERMAL_PAPER_WIDTH_MM, THERMAL_PAPER_HEIGHT_MM),
                QPageSize.Unit.Millimeter,
                "POS58 Receipt"
            )
            page_layout = QPageLayout(page_size, QPageLayout.Orientation.Portrait, QMarginsF(0, 0, 0, 0))
            
            self.web_view.page().printToPdf(pdf_generated_callback, page_layout)
            
        except Exception as e:
            logger.exception(f"Error handling save pdf request: {e}")

    # ─── Close Event ───────────────────────────────────────────────────

    def closeEvent(
        self,
        event,
    ):
        """Optionally create backup on close."""

        try:
            session = get_session()

            try:
                settings = (
                    SettingsRepository(
                        session
                    ).get_settings()
                )

                if settings.auto_backup:
                    BackupService().create_backup()

                    logger.info(
                        "Auto-backup created on exit"
                    )

            finally:
                session.close()

        except Exception as e:
            logger.error(
                f"Auto-backup failed: {e}"
            )

        from app.database.engine import close_db

        close_db()
        # Stop Worker Portal and Tunnel
        if hasattr(self, 'tunnel') and self.tunnel:
            self.tunnel.stop()
        if hasattr(self, 'worker_server') and self.worker_server:
            self.worker_server.stop()
            
        event.accept()
