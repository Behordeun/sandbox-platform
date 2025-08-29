import asyncio
import logging
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.config import settings
from app.middleware.auth import AuthMiddleware
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.logging import LoggingMiddleware
from app.core.system_logger import system_logger
from app.middleware.metrics import MetricsMiddleware, get_metrics
from app.middleware.rate_limit import RateLimitMiddleware
from app.services.discovery import service_discovery
from app.services.proxy import proxy_service
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.routing import APIRoute

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Sandbox API Gateway...")

    # Start background tasks
    health_check_task = asyncio.create_task(periodic_health_checks())

    yield

    # Shutdown
    logger.info("Shutting down Sandbox API Gateway...")
    health_check_task.cancel()
    await proxy_service.close()


async def periodic_health_checks():
    """Periodic health checks for services."""
    # Wait before starting health checks to allow services to start
    await asyncio.sleep(5)
    
    while True:
        try:
            await service_discovery.health_check_all_services()
            await asyncio.sleep(30)  # Check every 30 seconds
        except asyncio.CancelledError:
            # Perform any cleanup if needed, then re-raise
            raise
        except Exception as e:
            logger.error(f"Health check error: {e}")
            await asyncio.sleep(30)


# Custom unique operation id generator
def generate_unique_id(route: APIRoute) -> str:
    method = next(iter(route.methods)).lower() if route.methods else "get"
    tag = (route.tags[0] if route.tags else "api").replace(" ", "_")
    # Sanitize path: remove { } and replace / - with _
    path = (
        route.path_format.lstrip("/")
        .replace("/", "_")
        .replace("-", "_")
        .replace("{", "")
        .replace("}", "")
    ) or "root"
    name = (route.name or "handler").replace(" ", "_")
    return f"{tag}_{method}_{path}_{name}"

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API Gateway for the Sandbox Platform",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    generate_unique_id_function=generate_unique_id,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Correlation ID middleware should run early
app.add_middleware(CorrelationIdMiddleware)

# Add custom middleware (order matters!)
if settings.metrics_enabled:
    app.add_middleware(MetricsMiddleware)

if settings.request_logging_enabled or settings.response_logging_enabled:
    app.add_middleware(LoggingMiddleware)

# Only add rate limiting if Redis is available
if settings.rate_limit_enabled:
    try:
        import redis

        redis_client = redis.from_url(settings.redis_url)
        if redis_client is not None:
            redis_client.ping()
            app.add_middleware(RateLimitMiddleware)
        else:
            logger.warning("Redis client is None, disabling rate limiting.")
    except Exception as e:
        logger.warning(f"Redis not available, disabling rate limiting: {e}")

# Add authentication middleware (should be last)
app.add_middleware(AuthMiddleware)


# Startup log
system_logger.info("Service startup", {"service": settings.app_name, "version": settings.app_version})


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Metrics endpoint
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.metrics_enabled:
        return JSONResponse(status_code=404, content={"error": "Metrics not enabled"})
    return get_metrics()


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_url": "/health",
        "metrics_url": "/metrics" if settings.metrics_enabled else None,
    }


# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
