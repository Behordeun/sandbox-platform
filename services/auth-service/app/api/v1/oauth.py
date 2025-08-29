from typing import Any, Optional
from urllib.parse import urlencode, urlparse

from app.crud.oauth_client import oauth_client_crud
from app.crud.oauth_token import oauth_token_crud
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.oauth import OAuthClientCreate, OAuthClientResponse, TokenResponse
from fastapi import APIRouter, Depends, Form, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/clients", response_model=OAuthClientResponse)
def create_oauth_client(
    *,
    db: Session = Depends(get_db),
    client_in: OAuthClientCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a new OAuth2 client."""
    client = oauth_client_crud.create(db, obj_in=client_in)
    return client


@router.get("/clients/{client_id}", response_model=OAuthClientResponse)
def get_oauth_client(
    *,
    db: Session = Depends(get_db),
    client_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get OAuth2 client by ID."""
    client = oauth_client_crud.get_by_client_id(db, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="OAuth client not found")
    return client


def normalize_and_validate_redirect_uri(redirect_uri: str, client) -> str:
    from urllib.parse import urlparse, unquote

    def normalize_uri(uri: str) -> str:
        uri = uri.replace("\\", "").strip()
        parsed = urlparse(uri)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = unquote(parsed.path)
        normalized = f"{scheme}://{netloc}{path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized.rstrip("/")

    normalized_safe_redirect_uri = normalize_uri(redirect_uri)
    registered_uris = [normalize_uri(uri) for uri in client.redirect_uris]
    if normalized_safe_redirect_uri not in registered_uris:
        raise HTTPException(status_code=400, detail="Unsafe redirect URI")
    parsed = urlparse(normalized_safe_redirect_uri)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Unsafe redirect URI")
    return normalized_safe_redirect_uri

@router.get("/authorize")
def authorize(
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """OAuth2 authorization endpoint."""
    client = oauth_client_crud.get_by_client_id(db, client_id=client_id)
    if not client or not client.is_active:
        raise HTTPException(status_code=400, detail="Invalid client")

    if not oauth_client_crud.is_redirect_uri_valid(
        db, client_id=client_id, redirect_uri=redirect_uri
    ):
        raise HTTPException(status_code=400, detail="Invalid redirect URI")

    if not oauth_client_crud.supports_response_type(
        db, client_id=client_id, response_type=response_type
    ):
        raise HTTPException(status_code=400, detail="Unsupported response type")

    if response_type != "code":
        raise HTTPException(status_code=400, detail="Unsupported response type")

    token_obj = oauth_token_crud.create_authorization_code(
        db, user_id=current_user.id, client_id=client_id, scope=scope
    )

    params = {"code": token_obj.authorization_code}
    if state:
        params["state"] = state

    normalized_safe_redirect_uri = normalize_and_validate_redirect_uri(redirect_uri, client)
    parsed = urlparse(normalized_safe_redirect_uri)
    redirect_url = (
        f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params)}"
    )
    return RedirectResponse(url=redirect_url)


def handle_authorization_code_grant(db, client_id, code, redirect_uri):
    if not code or not redirect_uri:
        raise HTTPException(status_code=400, detail="Missing code or redirect_uri")
    if not oauth_client_crud.is_redirect_uri_valid(
        db, client_id=client_id, redirect_uri=redirect_uri
    ):
        raise HTTPException(status_code=400, detail="Invalid redirect URI")
    token_obj = oauth_token_crud.exchange_code_for_tokens(
        db, code=code, client_id=client_id
    )
    if not token_obj:
        raise HTTPException(status_code=400, detail="Invalid authorization code")
    return {
        "access_token": token_obj.access_token,
        "refresh_token": token_obj.refresh_token,
        "token_type": token_obj.token_type,
        "expires_in": int(
            (token_obj.expires_at - token_obj.created_at).total_seconds()
        ),
        "scope": token_obj.scope,
    }

def handle_refresh_token_grant(db, refresh_token):
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh_token")
    token_obj = oauth_token_crud.refresh_access_token(
        db, refresh_token=refresh_token
    )
    if not token_obj:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    return {
        "access_token": token_obj.access_token,
        "refresh_token": token_obj.refresh_token,
        "token_type": token_obj.token_type,
        "expires_in": int(
            (token_obj.expires_at - token_obj.updated_at).total_seconds()
        ),
        "scope": token_obj.scope,
    }

def handle_client_credentials_grant(db, client_id, client):
    token_obj = oauth_token_crud.create_client_credentials_token(
        db, client_id=client_id, scope=client.scope
    )
    return {
        "access_token": token_obj.access_token,
        "token_type": token_obj.token_type,
        "expires_in": int(
            (token_obj.expires_at - token_obj.created_at).total_seconds()
        ),
        "scope": token_obj.scope,
    }

@router.post("/token", response_model=TokenResponse)
def get_token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: Optional[str] = Form(None),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> Any:
    """OAuth2 token endpoint."""
    client = oauth_client_crud.authenticate_client(
        db, client_id=client_id, client_secret=client_secret or ""
    )
    if not client:
        raise HTTPException(status_code=401, detail="Invalid client credentials")
    if not oauth_client_crud.supports_grant_type(
        db, client_id=client_id, grant_type=grant_type
    ):
        raise HTTPException(status_code=400, detail="Unsupported grant type")

    if grant_type == "authorization_code":
        return handle_authorization_code_grant(db, client_id, code, redirect_uri)
    elif grant_type == "refresh_token":
        return handle_refresh_token_grant(db, refresh_token)
    elif grant_type == "client_credentials":
        return handle_client_credentials_grant(db, client_id, client)
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant type")
