from app.api.v1.router import api_router
from app.core.system_logger import system_logger
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Rate Limiter Service", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")


# Startup log
system_logger.info("Service startup", {"service": "rate-limiter-service"})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    system_logger.error(
        exc,
        {
            "path": str(request.url.path),
            "method": request.method,
            "client": getattr(request.client, "host", None),
        },
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        },
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rate-limiter-service"}
