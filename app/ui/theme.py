from __future__ import annotations
"""
Design system theme — translates the Stitch design reference into PySide6 QSS.

Colors, fonts, spacing, and the global stylesheet for the application.
Based on the Stitch / TailorMaster Offline design system.
"""

# ──────────────────────────────────────────────
# Color Palette
# ──────────────────────────────────────────────

COLORS = {
    # Primary
    "primary": "#091426",
    "primary_container": "#1e293b",
    "on_primary": "#ffffff",
    "on_primary_container": "#8590a6",

    # Surface
    "surface": "#f8f9ff",
    "surface_dim": "#cbdbf5",
    "surface_container_lowest": "#ffffff",
    "surface_container_low": "#eff4ff",
    "surface_container": "#e5eeff",
    "surface_container_high": "#dce9ff",
    "surface_container_highest": "#d3e4fe",
    "on_surface": "#0b1c30",
    "on_surface_variant": "#45474c",

    # Secondary
    "secondary": "#5d5f5b",
    "secondary_container": "#e0e0db",

    # Tertiary
    "tertiary": "#221000",
    "tertiary_container": "#3f2200",
    "tertiary_fixed": "#ffdcbd",
    "on_tertiary_container": "#b58759",

    # Error
    "error": "#ba1a1a",
    "error_container": "#ffdad6",
    "on_error": "#ffffff",
    "on_error_container": "#93000a",

    # Outline
    "outline": "#75777d",
    "outline_variant": "#c5c6cd",

    # Inverse
    "inverse_surface": "#213145",
    "inverse_on_surface": "#eaf1ff",

    # Status colors
    "status_new": "#64748b",
    "status_stitching": "#3b82f6",
    "status_ready": "#10b981",
    "status_delivered": "#6366f1",
    "status_cancelled": "#9ca3af",
    "status_overdue": "#ef4444",

    # Payment status
    "status_paid": "#10b981",
    "status_partial": "#f59e0b",
    "status_unpaid": "#ef4444",
}

# ──────────────────────────────────────────────
# Status badge color mapping
# ──────────────────────────────────────────────

STATUS_COLORS = {
    "NEW": ("#64748b", "#f1f5f9"),
    "STITCHING": ("#3b82f6", "#eff6ff"),
    "READY": ("#10b981", "#ecfdf5"),
    "DELIVERED": ("#6366f1", "#eef2ff"),
    "CANCELLED": ("#9ca3af", "#f9fafb"),
    "OVERDUE": ("#ef4444", "#fef2f2"),
    "PAID": ("#10b981", "#ecfdf5"),
    "PARTIALLY PAID": ("#f59e0b", "#fffbeb"),
    "UNPAID": ("#ef4444", "#fef2f2"),
}

# ──────────────────────────────────────────────
# Typography
# ──────────────────────────────────────────────

FONT_FAMILY = "Public Sans"
FALLBACK_FONT = "Segoe UI, Arial, sans-serif"

FONT_SIZES = {
    "display": 40,
    "headline_lg": 32,
    "headline_md": 24,
    "body_lg": 18,
    "body_md": 16,
    "label_lg": 16,
    "label_sm": 13,
}

# ──────────────────────────────────────────────
# Spacing
# ──────────────────────────────────────────────

SIDEBAR_WIDTH = 280
HEADER_HEIGHT = 72
CONTAINER_PADDING = 40
GUTTER = 24
STACK_SM = 8
STACK_MD = 16
STACK_LG = 32

# ──────────────────────────────────────────────
# Elevation / Shadows (as CSS border workaround)
# ──────────────────────────────────────────────

CARD_RADIUS = 12
BUTTON_RADIUS = 12
BADGE_RADIUS = 100  # pill shape

# ──────────────────────────────────────────────
# Global Stylesheet
# ──────────────────────────────────────────────

def get_global_stylesheet() -> str:
    """Return the global QSS stylesheet for the application."""
    return f"""
        /* ─── Global ─── */
        * {{
            font-family: "{FONT_FAMILY}", {FALLBACK_FONT};
        }}

        QMainWindow, QWidget {{
            background-color: {COLORS['surface']};
            color: {COLORS['on_surface']};
        }}

        /* ─── Scroll Areas ─── */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        QScrollBar:vertical {{
            background: {COLORS['surface_container_low']};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {COLORS['outline_variant']};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {COLORS['outline']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: {COLORS['surface_container_low']};
            height: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {COLORS['outline_variant']};
            border-radius: 4px;
            min-width: 30px;
        }}

        /* ─── Buttons ─── */
        QPushButton {{
            font-size: {FONT_SIZES['label_lg']}px;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: {BUTTON_RADIUS}px;
            border: 1px solid {COLORS['outline_variant']};
            background-color: {COLORS['surface_container_lowest']};
            color: {COLORS['on_surface']};
        }}
        QPushButton:hover {{
            background-color: {COLORS['surface_container_low']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['surface_container']};
        }}
        QPushButton:disabled {{
            color: {COLORS['outline']};
            background-color: {COLORS['surface_container_low']};
        }}

        /* ─── Primary Button ─── */
        QPushButton[cssClass="primary"] {{
            background-color: {COLORS['primary']};
            color: {COLORS['on_primary']};
            border: none;
        }}
        QPushButton[cssClass="primary"]:hover {{
            background-color: {COLORS['primary_container']};
        }}
        QPushButton[cssClass="primary"]:pressed {{
            background-color: #0d1f38;
        }}

        /* ─── Danger Button ─── */
        QPushButton[cssClass="danger"] {{
            background-color: {COLORS['error']};
            color: {COLORS['on_error']};
            border: none;
        }}
        QPushButton[cssClass="danger"]:hover {{
            background-color: #a11616;
        }}

        /* ─── Text Button ─── */
        QPushButton[cssClass="text"] {{
            background-color: transparent;
            border: none;
            color: {COLORS['primary']};
        }}
        QPushButton[cssClass="text"]:hover {{
            background-color: {COLORS['surface_container_low']};
        }}

        /* ─── Line Edits ─── */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            font-size: {FONT_SIZES['body_md']}px;
            padding: 10px 14px;
            border: 1px solid {COLORS['outline_variant']};
            border-radius: {CARD_RADIUS}px;
            background-color: {COLORS['surface']};
            color: {COLORS['on_surface']};
            selection-background-color: {COLORS['surface_container_highest']};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {COLORS['primary']};
        }}
        QLineEdit:disabled {{
            background-color: {COLORS['surface_container_low']};
            color: {COLORS['outline']};
        }}

        /* ─── ComboBox ─── */
        QComboBox {{
            font-size: {FONT_SIZES['body_md']}px;
            padding: 10px 14px;
            border: 1px solid {COLORS['outline_variant']};
            border-radius: {CARD_RADIUS}px;
            background-color: {COLORS['surface']};
            color: {COLORS['on_surface']};
        }}
        QComboBox:focus {{
            border: 2px solid {COLORS['primary']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {COLORS['surface_container_lowest']};
            border: 1px solid {COLORS['outline_variant']};
            border-radius: 8px;
            padding: 4px;
            selection-background-color: {COLORS['surface_container']};
            selection-color: {COLORS['on_surface']};
        }}

        /* ─── SpinBox ─── */
        QSpinBox, QDoubleSpinBox {{
            font-size: {FONT_SIZES['body_md']}px;
            padding: 10px 14px;
            border: 1px solid {COLORS['outline_variant']};
            border-radius: {CARD_RADIUS}px;
            background-color: {COLORS['surface']};
        }}

        /* ─── DateEdit ─── */
        QDateEdit {{
            font-size: {FONT_SIZES['body_md']}px;
            padding: 10px 14px;
            border: 1px solid {COLORS['outline_variant']};
            border-radius: {CARD_RADIUS}px;
            background-color: {COLORS['surface']};
        }}
        QDateEdit:focus {{
            border: 2px solid {COLORS['primary']};
        }}

        /* ─── Labels ─── */
        QLabel {{
            color: {COLORS['on_surface']};
            background-color: transparent;
        }}
        QLabel[cssClass="heading"] {{
            font-size: {FONT_SIZES['headline_md']}px;
            font-weight: 600;
            color: {COLORS['primary']};
        }}
        QLabel[cssClass="subheading"] {{
            font-size: {FONT_SIZES['body_lg']}px;
            font-weight: 400;
            color: {COLORS['on_surface_variant']};
        }}
        QLabel[cssClass="field-label"] {{
            font-size: {FONT_SIZES['label_lg']}px;
            font-weight: 600;
            color: {COLORS['on_surface']};
        }}
        QLabel[cssClass="error"] {{
            font-size: {FONT_SIZES['label_sm']}px;
            color: {COLORS['error']};
        }}
        QLabel[cssClass="muted"] {{
            font-size: {FONT_SIZES['label_sm']}px;
            color: {COLORS['on_surface_variant']};
        }}

        /* ─── Group Box ─── */
        QGroupBox {{
            font-size: {FONT_SIZES['label_lg']}px;
            font-weight: 600;
            border: 1px solid {COLORS['outline_variant']};
            border-radius: {CARD_RADIUS}px;
            margin-top: 12px;
            padding-top: 20px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
        }}

        /* ─── Table Widget ─── */
        QTableWidget {{
            background-color: {COLORS['surface_container_lowest']};
            border: 1px solid {COLORS['surface_container_low']};
            border-radius: {CARD_RADIUS}px;
            gridline-color: {COLORS['surface_container']};
            font-size: {FONT_SIZES['body_md']}px;
        }}
        QTableWidget::item {{
            padding: 12px 16px;
            border-bottom: 1px solid {COLORS['surface_container']};
        }}
        QTableWidget::item:selected {{
            background-color: {COLORS['surface_container']};
            color: {COLORS['on_surface']};
        }}
        QTableWidget::item:hover {{
            background-color: {COLORS['surface_container_low']};
        }}
        QHeaderView::section {{
            background-color: {COLORS['surface_container_low']};
            color: {COLORS['on_surface_variant']};
            font-size: {FONT_SIZES['label_sm']}px;
            font-weight: 600;
            text-transform: uppercase;
            padding: 12px 16px;
            border: none;
            border-bottom: 1px solid {COLORS['surface_container']};
        }}

        /* ─── Tab Widget ─── */
        QTabWidget::pane {{
            border: 1px solid {COLORS['outline_variant']};
            border-radius: {CARD_RADIUS}px;
            background-color: {COLORS['surface_container_lowest']};
        }}
        QTabBar::tab {{
            padding: 10px 20px;
            font-size: {FONT_SIZES['label_lg']}px;
            font-weight: 500;
            color: {COLORS['on_surface_variant']};
            border: none;
            border-bottom: 2px solid transparent;
        }}
        QTabBar::tab:selected {{
            color: {COLORS['primary']};
            border-bottom: 2px solid {COLORS['primary']};
        }}
        QTabBar::tab:hover {{
            color: {COLORS['on_surface']};
            background-color: {COLORS['surface_container_low']};
        }}

        /* ─── Dialog ─── */
        QDialog {{
            background-color: {COLORS['surface_container_lowest']};
            border-radius: {CARD_RADIUS}px;
        }}

        /* ─── Message Box ─── */
        QMessageBox {{
            background-color: {COLORS['surface_container_lowest']};
        }}
        QMessageBox QPushButton {{
            min-width: 80px;
        }}

        /* ─── Tooltip ─── */
        QToolTip {{
            background-color: {COLORS['inverse_surface']};
            color: {COLORS['inverse_on_surface']};
            border: none;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: {FONT_SIZES['label_sm']}px;
        }}
    """
