from __future__ import annotations
"""Application configuration — paths, constants, platform-aware directories."""

import os
import sys
import platform

APP_NAME = "TailorShopManager"
APP_VERSION = "1.0.0"
APP_DISPLAY_NAME = "Tailor Shop Manager"

# ---------------------------------------------------------------------------
# Platform-aware data directory
# ---------------------------------------------------------------------------

def _get_app_data_dir() -> str:
    """Return the platform-appropriate application data directory."""
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif system == "Darwin":  # macOS
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:  # Linux and others
        base = os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share"))
    return os.path.join(base, APP_NAME)


APP_DATA_DIR = _get_app_data_dir()
DATABASE_DIR = os.path.join(APP_DATA_DIR, "data")
DATABASE_PATH = os.path.join(DATABASE_DIR, "tailor_shop.db")
LOG_DIR = os.path.join(APP_DATA_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "tailor_shop.log")
BACKUP_DEFAULT_DIR = os.path.join(APP_DATA_DIR, "backups")
UPLOADS_DIR = os.path.join(APP_DATA_DIR, "uploads")

# ---------------------------------------------------------------------------
# Ensure directories exist
# ---------------------------------------------------------------------------

def ensure_dirs():
    """Create all required application directories if they don't exist."""
    for d in [APP_DATA_DIR, DATABASE_DIR, LOG_DIR, BACKUP_DEFAULT_DIR, UPLOADS_DIR]:
        os.makedirs(d, exist_ok=True)
        
    # Migrate any existing uploads from assets to APP_DATA_DIR
    import shutil
    base_dir = os.path.dirname(os.path.abspath(__file__))
    old_uploads = os.path.join(base_dir, "assets", "www", "uploads")
    if os.path.exists(old_uploads) and os.listdir(old_uploads):
        try:
            for item in os.listdir(old_uploads):
                src = os.path.join(old_uploads, item)
                dst = os.path.join(UPLOADS_DIR, item)
                if os.path.isdir(src):
                    if not os.path.exists(dst):
                        shutil.copytree(src, dst)
                    else:
                        # Copy contents if dir exists
                        for sub_item in os.listdir(src):
                            shutil.copy2(os.path.join(src, sub_item), os.path.join(dst, sub_item))
                else:
                    shutil.copy2(src, dst)
            # Remove old directory after successful copy
            shutil.rmtree(old_uploads)
            print(f"Migrated uploads from {old_uploads} to {UPLOADS_DIR}")
        except Exception as e:
            print(f"Warning: Failed to migrate old uploads: {e}")


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

def _get_assets_dir() -> str:
    """Return path to bundled assets (works both in dev and PyInstaller)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.join(sys._MEIPASS, "assets")  # type: ignore[attr-defined]
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


ASSETS_DIR = _get_assets_dir()
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# ---------------------------------------------------------------------------
# Order number format
# ---------------------------------------------------------------------------

ORDER_NUMBER_PREFIX = "ORD"
ORDER_NUMBER_FORMAT = "{prefix}-{seq:06d}"  # ORD-000001

# ---------------------------------------------------------------------------
# Measurement templates
# ---------------------------------------------------------------------------

MEASUREMENT_TEMPLATES = {
    "Shirt": [
        "Length", "Shoulder", "Chest", "Waist", "Hip",
        "Sleeve Length", "Bicep", "Cuff", "Collar",
        "Front Length", "Back Length",
    ],
    "Pant": [
        "Length", "Waist", "Hip", "Thigh", "Knee",
        "Bottom", "Rise",
    ],
    "Kurta": [
        "Length", "Shoulder", "Chest", "Waist", "Hip",
        "Sleeve Length", "Bicep", "Cuff", "Collar",
        "Front Length", "Back Length",
    ],
    "Blouse": [
        "Length", "Shoulder", "Bust", "Waist", "Sleeve",
        "Armhole", "Neck Front", "Neck Back",
    ],
    "Suit": [
        "Length", "Shoulder", "Chest", "Waist", "Hip",
        "Sleeve Length", "Bicep", "Cuff", "Collar",
        "Front Length", "Back Length",
        "Pant Length", "Pant Waist", "Pant Hip", "Pant Thigh",
        "Pant Knee", "Pant Bottom", "Pant Rise",
    ],
    "Custom": [],  # user-defined fields
}

# ---------------------------------------------------------------------------
# Order statuses
# ---------------------------------------------------------------------------

ORDER_STATUSES = ["NEW", "CUTTING_COMPLETE", "STITCHING_COMPLETE", "DELIVERED", "CANCELLED"]
PAYMENT_METHODS = ["Cash", "UPI", "Card", "Other"]
PAYMENT_STATUSES = ["UNPAID", "PARTIALLY PAID", "PAID"]
EXPENSE_CATEGORIES = ["Material", "Electricity", "Rent", "Salary", "Transport", "Other"]

# ---------------------------------------------------------------------------
# Default settings
# ---------------------------------------------------------------------------

DEFAULT_CURRENCY = "₹"
DEFAULT_MEASUREMENT_UNIT = "inches"
DEFAULT_DATE_FORMAT = "DD/MM/YYYY"
DEFAULT_PAPER_SIZE = "A4"
