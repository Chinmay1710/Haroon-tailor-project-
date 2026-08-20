from __future__ import annotations
"""Tailor Shop Manager — main entry point."""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import Qt

from app.config import ensure_dirs, FONTS_DIR, APP_DISPLAY_NAME
from app.utils.logger import get_logger

logger = get_logger("main")


def load_fonts():
    """Load custom fonts bundled with the application."""
    if os.path.isdir(FONTS_DIR):
        for font_file in os.listdir(FONTS_DIR):
            if font_file.endswith((".ttf", ".otf")):
                path = os.path.join(FONTS_DIR, font_file)
                font_id = QFontDatabase.addApplicationFont(path)
                if font_id >= 0:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    logger.info(f"Loaded font: {families}")


def main():
    """Application entry point."""
    # Create required directories
    ensure_dirs()

    logger.info(f"Starting {APP_DISPLAY_NAME}...")

    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_DISPLAY_NAME)
    app.setOrganizationName("TailorShop")

    # Set default font
    default_font = QFont("Public Sans", 14)
    default_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(default_font)

    # Load custom fonts
    load_fonts()

    # Create and show the main window
    from app.ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    logger.info("Application window shown")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
