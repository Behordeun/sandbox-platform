from app.api.v1.router import api_router
from app.core.config import settings
from fastapi import FastAPI
from fastapi.routing import APIRoute


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


app = FastAPI(title=settings.app_name, version=settings.app_version, generate_unique_id_function=generate_unique_id)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nin-service"}
