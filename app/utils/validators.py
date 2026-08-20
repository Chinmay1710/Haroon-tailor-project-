from __future__ import annotations
"""Input validation helpers."""

import re


def validate_required(field_name: str, value: str) -> str | None:
    """Return error message if value is empty, else None."""

    if not value or not value.strip():
        return f"{field_name} is required"
    return None


def validate_mobile(mobile: str) -> str | None:
    """Validate mobile number format (optional field — empty is OK)."""
    if not mobile or not mobile.strip():
        return None  # optional
    cleaned = re.sub(r'[\s\-\(\)\+]', '', mobile)
    if not cleaned.isdigit():
        return "Mobile number should contain only digits"
    if len(cleaned) < 7 or len(cleaned) > 15:
        return "Mobile number should be 7-15 digits"
    return None


def validate_amount(value: str, field_name: str = "Amount",
                    allow_zero: bool = False) -> tuple[float | None, str | None]:
    """
    Validate a numeric amount.
    Returns (parsed_float, error_message).
    """
    if not value or not value.strip():
        return None, f"{field_name} is required"
    try:
        amount = float(value)
    except (ValueError, TypeError):
        return None, f"{field_name} must be a valid number"
    if amount < 0:
        return None, f"{field_name} cannot be negative"
    if not allow_zero and amount == 0:
        return None, f"{field_name} must be greater than 0"
    return amount, None


def validate_positive_int(value: str, field_name: str = "Quantity") -> tuple[int | None, str | None]:
    """Validate a positive integer. Returns (parsed_int, error_message)."""
    if not value or not value.strip():
        return None, f"{field_name} is required"
    try:
        num = int(value)
    except (ValueError, TypeError):
        return None, f"{field_name} must be a whole number"
    if num <= 0:
        return None, f"{field_name} must be greater than 0"
    return num, None


def validate_advance(advance: float, total: float) -> str | None:
    """Validate that advance doesn't exceed total."""
    if advance < 0:
        return "Advance cannot be negative"
    if advance > total:
        return "Advance cannot exceed the total amount"
    return None
