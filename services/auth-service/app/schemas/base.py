from typing import Any, Optional
from pydantic import BaseModel


class DPIResponse(BaseModel):
    """Standard DPI API response format"""
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None


class DPIError(BaseModel):
    """Standard DPI error response"""
    success: bool = False
    message: str
    error_code: str
    details: Optional[dict] = None