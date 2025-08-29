import os
import asyncio
from typing import Any, Dict

from sqlalchemy import create_engine, text


_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return None
        _engine = create_engine(db_url, pool_pre_ping=True)
    return _engine


async def insert_gateway_access_log(log: Dict[str, Any]) -> None:
    engine = _get_engine()
    if engine is None:
        return

    def _insert_sync():
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO gateway_access_logs (
                        request_id, user_id, auth_method, service_name,
                        method, path, status_code, duration_ms,
                        client_ip, user_agent
                    ) VALUES (
                        :request_id, :user_id, :auth_method, :service_name,
                        :method, :path, :status_code, :duration_ms,
                        :client_ip, :user_agent
                    )
                    """
                ),
                {
                    "request_id": str(log.get("request_id") or ""),
                    "user_id": str(log.get("user_id") or ""),
                    "auth_method": str(log.get("auth_method") or ""),
                    "service_name": str(log.get("service") or ""),
                    "method": str(log.get("method") or ""),
                    "path": str(log.get("path") or ""),
                    "status_code": int(log.get("status_code") or 0),
                    "duration_ms": int(log.get("duration_ms") or 0),
                    "client_ip": str(log.get("client_ip") or ""),
                    "user_agent": str(log.get("user_agent") or ""),
                },
            )

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, _insert_sync)
    except Exception:
        # Swallow DB logging errors to avoid impacting request path
        pass

