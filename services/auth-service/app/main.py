import logging
from contextlib import asynccontextmanager
from typing import Any

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.system_logger import system_logger
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.logging import UserActivityLoggingMiddleware
from app.models import oauth_token  # Import to register models
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Sandbox Auth Service...")
    logger.info(f"Database URL: {settings.database_url}")

    # Also log to system_logger with rich context
    system_logger.info(
        "Auth service startup",
        {
            "service": settings.app_name,
            "version": settings.app_version,
            "database_url": settings.database_url,
        },
    )

    # Tables are managed by Alembic migrations
    # Base.metadata.create_all(bind=engine)
    logger.info("Database connection verified")

    # Test database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        system_logger.error(e, {"stage": "startup", "check": "db"}, exc_info=True)

    yield

    # Shutdown
    logger.info("Shutting down Sandbox Auth Service...")
    system_logger.info("Auth service shutdown", {"service": settings.app_name})


# Custom unique operation id generator
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


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Authentication and Authorization service for the Sandbox Platform",
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

# Add correlation and user activity logging middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(UserActivityLoggingMiddleware)

# Metrics instrumentation (Prometheus)
try:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
except Exception:
    # Keep service running even if instrumentation fails
    pass


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_url": "/health",
    }


# Well-known endpoints for OAuth2/OIDC discovery
@app.get("/.well-known/openid_configuration")
async def openid_configuration():
    """OpenID Connect Discovery endpoint."""
    return {
        "issuer": settings.oauth2_issuer_url,
        "authorization_endpoint": f"{settings.oauth2_issuer_url}/api/v1/oauth2/authorize",
        "token_endpoint": f"{settings.oauth2_issuer_url}/api/v1/oauth2/token",
        "userinfo_endpoint": f"{settings.oauth2_issuer_url}/api/v1/auth/userinfo",
        "jwks_uri": settings.oauth2_jwks_uri,
        "response_types_supported": ["code", "token"],
        "grant_types_supported": [
            "authorization_code",
            "refresh_token",
            "client_credentials",
        ],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["HS256"],
        "scopes_supported": ["openid", "profile", "email"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_post",
            "client_secret_basic",
        ],
        "claims_supported": ["sub", "email", "name", "preferred_username"],
    }


@app.get("/.well-known/jwks.json")
async def jwks():
    """JSON Web Key Set endpoint."""
    # In a production environment, you would return actual JWKs
    # For now, return an empty set since we're using symmetric keys
    return {"keys": []}


# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Global exception handlers
from fastapi import Request


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> Any:
    """Global exception handler for unhandled exceptions with rich logs."""
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
