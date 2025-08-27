import re
import html
from typing import Optional


def validate_nigerian_phone(phone: str) -> bool:
    """Validate Nigerian phone number format"""
    pattern = r"^(\+234|0)[7-9][0-1]\d{8}$"
    return bool(re.match(pattern, phone))


def validate_nin(nin: str) -> bool:
    """Validate NIN format (11 digits)"""
    return bool(re.match(r"^\d{11}$", nin))


def validate_bvn(bvn: str) -> bool:
    """Validate BVN format (11 digits)"""
    return bool(re.match(r"^\d{11}$", bvn))


def format_nigerian_phone(phone: str) -> Optional[str]:
    """Format Nigerian phone to international format"""
    # Sanitize input to prevent XSS
    phone = html.escape(phone)
    phone = re.sub(r"[^\d+]", "", phone)

    if phone.startswith("0"):
        return f"+234{phone[1:]}"
    elif phone.startswith("234"):
        return f"+{phone}"
    elif phone.startswith("+234"):
        return phone

    return None
