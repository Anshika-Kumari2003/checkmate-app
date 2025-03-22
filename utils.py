# utils.py
from datetime import datetime
import re

def format_date(date_str):
    """Converts various date formats to YYYY-MM-DD."""
    date_str = str(date_str).strip()
    # Handle MMDDYYYY format (e.g., "01162024" -> "2024-01-16")
    if len(date_str) == 8 and date_str.isdigit():
        try:
            return datetime.strptime(date_str, "%m%d%Y").strftime("%Y-%m-%d")
        except ValueError:
            pass
    valid_formats = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y", "%d %m %Y"]
    for fmt in valid_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"🚨 Invalid date format: {date_str}. Please use MMDDYYYY, DD-MM-YYYY, or YYYY-MM-DD.")

def clean_amount(amount_str):
    """Converts amount to a float after cleaning symbols and commas."""
    if not amount_str:
        return 0.0
    amount_str = re.sub(r"[^\d.]", "", amount_str)
    try:
        return float(amount_str)
    except ValueError:
        return 0.0