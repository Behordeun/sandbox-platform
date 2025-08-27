"""
Rotational and Persistent Logging System for DPI Sandbox Platform
Provides structured logging with automatic rotation and long-term persistence
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class DPIRotationalLogger:
    """Enhanced logging system with rotation and persistence for audit trails"""
    
    def __init__(self, service_name: str, log_dir: str = "logs"):
        self.service_name = service_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create archive directory for rotated logs
        self.archive_dir = self.log_dir / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        self.loggers = {}
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Setup different loggers for various audit categories"""
        
        log_configs = {
            'user_activity': {
                'filename': f'{self.service_name}_user_activity.log',
                'max_bytes': 50 * 1024 * 1024,  # 50MB
                'backup_count': 10,
                'level': logging.INFO
            },
            'api_access': {
                'filename': f'{self.service_name}_api_access.log',
                'max_bytes': 100 * 1024 * 1024,  # 100MB
                'backup_count': 15,
                'level': logging.INFO
            },
            'security_events': {
                'filename': f'{self.service_name}_security.log',
                'max_bytes': 25 * 1024 * 1024,  # 25MB
                'backup_count': 20,  # Keep more security logs
                'level': logging.WARNING
            },
            'service_health': {
                'filename': f'{self.service_name}_health.log',
                'max_bytes': 20 * 1024 * 1024,  # 20MB
                'backup_count': 5,
                'level': logging.INFO
            },
            'audit_trail': {
                'filename': f'{self.service_name}_audit.log',
                'max_bytes': 75 * 1024 * 1024,  # 75MB
                'backup_count': 25,  # Long-term audit retention
                'level': logging.INFO
            }
        }
        
        for log_type, config in log_configs.items():
            logger = logging.getLogger(f"{self.service_name}_{log_type}")
            logger.setLevel(config['level'])
            
            # Remove existing handlers
            logger.handlers.clear()
            
            # Rotating file handler
            log_file = self.log_dir / config['filename']
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=config['max_bytes'],
                backupCount=config['backup_count']
            )
            
            # JSON formatter for structured logging
            formatter = logging.Formatter(
                '%(message)s'  # We'll format JSON ourselves
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Also add console handler for development
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            self.loggers[log_type] = logger
    
    def log_user_activity(self, user_id: str, activity: str, details: Dict[str, Any]):
        """Log user activity with structured data"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "log_type": "user_activity",
            "user_id": user_id,
            "activity": activity,
            "details": details,
            "session_id": details.get("session_id"),
            "ip_address": details.get("ip_address"),
            "user_agent": details.get("user_agent")
        }
        self.loggers['user_activity'].info(json.dumps(log_entry))
    
    def log_api_access(self, method: str, path: str, status_code: int, 
                      duration_ms: float, user_id: Optional[str] = None, **kwargs):
        """Log API access with performance metrics"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "log_type": "api_access",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "success": 200 <= status_code < 400,
            **kwargs
        }
        self.loggers['api_access'].info(json.dumps(log_entry))
    
    def log_security_event(self, event_type: str, severity: str, details: Dict[str, Any]):
        """Log security events for audit and monitoring"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "log_type": "security_event",
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "requires_attention": severity in ["HIGH", "CRITICAL"]
        }
        
        if severity == "CRITICAL":
            self.loggers['security_events'].critical(json.dumps(log_entry))
        elif severity == "HIGH":
            self.loggers['security_events'].error(json.dumps(log_entry))
        else:
            self.loggers['security_events'].warning(json.dumps(log_entry))
    
    def log_service_health(self, component: str, status: str, metrics: Dict[str, Any]):
        """Log service health and performance metrics"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "log_type": "service_health",
            "component": component,
            "status": status,
            "metrics": metrics,
            "healthy": status == "healthy"
        }
        self.loggers['service_health'].info(json.dumps(log_entry))
    
    def log_audit_trail(self, action: str, resource: str, user_id: str, 
                       before_state: Optional[Dict] = None, 
                       after_state: Optional[Dict] = None, **kwargs):
        """Log audit trail for compliance and tracking"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "log_type": "audit_trail",
            "action": action,
            "resource": resource,
            "user_id": user_id,
            "before_state": before_state,
            "after_state": after_state,
            "change_summary": self._generate_change_summary(before_state, after_state),
            **kwargs
        }
        self.loggers['audit_trail'].info(json.dumps(log_entry))
    
    def _generate_change_summary(self, before: Optional[Dict], after: Optional[Dict]) -> Optional[str]:
        """Generate human-readable change summary"""
        if not before or not after:
            return None
        
        changes = []
        for key in set(before.keys()) | set(after.keys()):
            if key not in before:
                changes.append(f"Added {key}: {after[key]}")
            elif key not in after:
                changes.append(f"Removed {key}: {before[key]}")
            elif before[key] != after[key]:
                changes.append(f"Changed {key}: {before[key]} → {after[key]}")
        
        return "; ".join(changes) if changes else "No changes detected"
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about log files and rotation"""
        stats = {}
        for log_type in self.loggers.keys():
            log_file = self.log_dir / f"{self.service_name}_{log_type}.log"
            if log_file.exists():
                stat = log_file.stat()
                stats[log_type] = {
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "rotated_files": len(list(self.log_dir.glob(f"{log_file.name}.*")))
                }
        return stats


# Global logger instances for each service
_loggers: Dict[str, DPIRotationalLogger] = {}


def get_logger(service_name: str, log_dir: str = "logs") -> DPIRotationalLogger:
    """Get or create a rotational logger for a service"""
    if service_name not in _loggers:
        _loggers[service_name] = DPIRotationalLogger(service_name, log_dir)
    return _loggers[service_name]


# Convenience functions for common logging patterns
def log_nigerian_dpi_activity(service: str, user_id: str, dpi_service: str, 
                             action: str, nin_bvn: Optional[str] = None, **kwargs):
    """Specialized logging for Nigerian DPI activities"""
    logger = get_logger(service)
    details = {
        "dpi_service": dpi_service,
        "action": action,
        "nin_bvn_hash": hash(nin_bvn) if nin_bvn else None,  # Hash for privacy
        "nigerian_context": True,
        **kwargs
    }
    logger.log_user_activity(user_id, f"DPI_{dpi_service}_{action}", details)


def log_startup_access(service: str, startup_name: str, user_id: str, 
                      api_endpoint: str, **kwargs):
    """Specialized logging for Nigerian startup API access"""
    logger = get_logger(service)
    details = {
        "startup_name": startup_name,
        "api_endpoint": api_endpoint,
        "access_type": "startup_api_access",
        **kwargs
    }
    logger.log_user_activity(user_id, "STARTUP_API_ACCESS", details)