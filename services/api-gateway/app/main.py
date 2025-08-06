from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from contextlib import asynccontextmanager
import asyncio
import logging

from app.core.config import settings
from app.api.v1.router import api_router
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.metrics import MetricsMiddleware, get_metrics
from app.services.health import health_service
from app.services.discovery import service_discovery
from app.services.proxy import proxy_service

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
    while True:
        try:
            await service_discovery.health_check_all_services()
            await asyncio.sleep(30)  # Check every 30 seconds
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health check error: {e}")
            await asyncio.sleep(30)


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API Gateway for the Sandbox Platform",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add custom middleware (order matters!)
if settings.metrics_enabled:
    app.add_middleware(MetricsMiddleware)

if settings.request_logging_enabled or settings.response_logging_enabled:
    app.add_middleware(LoggingMiddleware)

if settings.rate_limit_enabled:
    app.add_middleware(RateLimitMiddleware)

# Add authentication middleware (should be last)
app.add_middleware(AuthMiddleware)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return await health_service.get_gateway_health()


# Metrics endpoint
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.metrics_enabled:
        return JSONResponse(
            status_code=404,
            content={"error": "Metrics not enabled"}
        )
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
        "metrics_url": "/metrics" if settings.metrics_enabled else None
    }


# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

