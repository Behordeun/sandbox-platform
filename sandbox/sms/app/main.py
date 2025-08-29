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


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    generate_unique_id_function=generate_unique_id,
)


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
