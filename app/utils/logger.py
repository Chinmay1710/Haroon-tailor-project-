from __future__ import annotations
"""Logging utility — file-based error logging with rotation."""

import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import LOG_FILE, LOG_DIR


def get_logger(name: str = "tailor_shop") -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)

        # File handler with rotation (5MB max, keep 3 backups)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

        # Console handler (for development)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter("%(levelname)-8s | %(message)s")
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

    return logger
