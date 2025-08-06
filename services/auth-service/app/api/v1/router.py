from app.api.v1 import auth, nin_bvn, oauth
from fastapi import APIRouter

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(oauth.router, prefix="/oauth2", tags=["oauth2"])
api_router.include_router(
    nin_bvn.router, prefix="/identity", tags=["identity-verification"]
)
