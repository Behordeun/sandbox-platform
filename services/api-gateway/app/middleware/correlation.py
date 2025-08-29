import uuid

from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Ensures each request has a correlation/request ID.

    - Reads existing `X-Request-ID` header if provided by client/upstream
    - Otherwise generates a UUID4
    - Stores on `request.state.request_id`
    - Adds `X-Request-ID` to the response headers
    """

    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
