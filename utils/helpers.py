"""
Utility and helper functions for X Assistant.
Provides text sanitization, language detection, and timestamp formatting.
"""

import re
from datetime import datetime


def clean_text(text: str) -> str:
    """Strip extra spaces and normalize text."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def is_bangla_text(text: str) -> bool:
    """Check if input string contains Unicode Bangla characters."""
    if not text:
        return False
    # Unicode range for Bangla script: U+0980 to U+09FF
    return bool(re.search(r"[\u0980-\u09FF]", text))


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime object into clean string."""
    dt = dt or datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def sanitize_filename(name: str) -> str:
    """Remove unsafe characters from string for file saving."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")
