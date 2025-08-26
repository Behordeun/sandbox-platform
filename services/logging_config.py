import logging
import logging.config
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "stream": "ext://sys.stdout",
        },
        "user_activity_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "logs/user_activity.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "security_events_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "logs/security_events.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
        },
        "api_access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "logs/api_access.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "service_health_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "logs/service_health.log",
            "maxBytes": 5242880,  # 5MB
            "backupCount": 3,
        },
    },
    "loggers": {
        "auth_service.user_activity": {
            "level": "INFO",
            "handlers": ["console", "user_activity_file"],
            "propagate": False,
        },
        "auth_service.security": {
            "level": "INFO",
            "handlers": ["console", "security_events_file"],
            "propagate": False,
        },
        "api_gateway.access": {
            "level": "INFO",
            "handlers": ["console", "api_access_file"],
            "propagate": False,
        },
        "service.health": {
            "level": "INFO",
            "handlers": ["console", "service_health_file"],
            "propagate": False,
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}


def setup_logging():
    """Setup logging configuration for the entire platform."""
    logging.config.dictConfig(LOGGING_CONFIG)

    # Create a startup log entry
    logger = logging.getLogger("platform.startup")
    logger.info(f"Logging system initialized at {datetime.now()}")
    logger.info("Log files created:")
    logger.info("  - logs/user_activity.log: User activities and interactions")
    logger.info("  - logs/security_events.log: Authentication and security events")
    logger.info("  - logs/api_access.log: API Gateway access logs")
    logger.info("  - logs/service_health.log: Service health and monitoring")


if __name__ == "__main__":
    setup_logging()
