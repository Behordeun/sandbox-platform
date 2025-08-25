import logging
import json
from datetime import datetime
from typing import Optional

# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_handler = logging.FileHandler("audit.log")
audit_formatter = logging.Formatter('%(asctime)s - %(message)s')
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)


def log_identity_verification(
    user_id: int,
    verification_type: str,
    identifier: str,
    success: bool,
    ip_address: Optional[str] = None
):
    """Log identity verification attempts"""
    audit_data = {
        "event": "identity_verification",
        "user_id": user_id,
        "type": verification_type,
        "identifier_hash": hash(identifier),  # Don't log actual NIN/BVN
        "success": success,
        "ip_address": ip_address,
        "timestamp": datetime.now().isoformat()
    }
    audit_logger.info(json.dumps(audit_data))


def log_auth_event(
    event_type: str,
    user_id: Optional[int] = None,
    email: Optional[str] = None,
    success: bool = True,
    ip_address: Optional[str] = None
):
    """Log authentication events"""
    audit_data = {
        "event": event_type,
        "user_id": user_id,
        "email": email,
        "success": success,
        "ip_address": ip_address,
        "timestamp": datetime.now().isoformat()
    }
    audit_logger.info(json.dumps(audit_data))