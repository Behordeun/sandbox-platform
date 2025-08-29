from app.core.config import settings
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.system_logger import system_logger
from fastapi.routing import APIRoute
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.access_log import AccessLogMiddleware


def generate_unique_id(route: APIRoute) -> str:
    method = next(iter(route.methods)).lower() if route.methods else "get"
    tag = (route.tags[0] if route.tags else "api").replace(" ", "_")
    path = (
        route.path_format.lstrip("/")
        .replace("/", "_")
        .replace("-", "_")
        .replace("{", "")
        .replace("}", "")
    ) or "root"
    name = (route.name or "handler").replace(" ", "_")
    return f"{tag}_{method}_{path}_{name}"


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    generate_unique_id_function=generate_unique_id,
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(AccessLogMiddleware)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.host, port=settings.port, reload=settings.debug
    )
else:
    # Startup log when imported by uvicorn
    try:
        system_logger.info("Service startup", {"service": settings.app_name, "version": settings.app_version})
    except Exception:
        pass

from fastapi import Request


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
        content={"error": "Internal server error", "message": "An unexpected error occurred"},
    )
