from __future__ import annotations
"""Formatting helpers — currency, dates, order numbers."""

from datetime import date, datetime


def format_currency(amount: float, symbol: str = "₹") -> str:
    """Format amount as currency string with thousands separator."""

    if amount == int(amount):
        return f"{symbol}{int(amount):,}"
    return f"{symbol}{amount:,.2f}"


def format_date(d: date | datetime | None, fmt: str = "DD/MM/YYYY") -> str:
    """Format a date using the specified format string."""
    if d is None:
        return "—"
    py_fmt = fmt.replace("DD", "%d").replace("MM", "%m").replace("YYYY", "%Y")
    return d.strftime(py_fmt)


def format_date_display(d: date | datetime | None) -> str:
    """Format date for display: '16 Aug 2026'."""
    if d is None:
        return "—"
    return d.strftime("%d %b %Y")


def format_order_number(seq: int) -> str:
    """Format order sequence number: ORD-000001."""
    return f"ORD-{seq:06d}"


def get_initials(name: str) -> str:
    """Get initials from a name (up to 2 characters)."""
    if not name:
        return "?"
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][0].upper()


def get_greeting() -> str:
    """Get time-of-day greeting."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    return "Good Evening"
