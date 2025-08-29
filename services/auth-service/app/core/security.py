from datetime import timedelta
from typing import Any, Optional, Union

from jose import JWTError, jwt
from urllib.parse import urlparse, urlunparse
from passlib.context import CryptContext

from .yaml_config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token with dynamic claims."""
    import secrets
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode = {
        "exp": expire,
        "iat": now,
        "nbf": now,
        "sub": str(subject),
        "type": "access",
        "jti": secrets.token_urlsafe(32),  # Unique token ID
        "iss": settings.oauth2_issuer_url,
        "aud": "sandbox-platform",
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token with dynamic claims."""
    import secrets
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)

    to_encode = {
        "exp": expire,
        "iat": now,
        "nbf": now,
        "sub": str(subject),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32),  # Unique token ID
        "iss": settings.oauth2_issuer_url,
        "aud": "sandbox-platform",
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def _issuer_aliases(primary: str) -> set[str]:
    """Return a set of acceptable issuer aliases for local dev convenience.

    Adds localhost/127.0.0.1 equivalents with the same scheme and port.
    """
    aliases = {primary}
    try:
        p = urlparse(primary)
        if p.hostname in {"localhost", "127.0.0.1"}:
            alt_host = "127.0.0.1" if p.hostname == "localhost" else "localhost"
            aliases.add(urlunparse((p.scheme, f"{alt_host}:{p.port}" if p.port else alt_host, p.path, p.params, p.query, p.fragment)))
    except Exception:
        pass
    return aliases


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify JWT token and return payload with enhanced validation."""
    try:
        # First attempt strict validation including issuer
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience="sandbox-platform",
            issuer=settings.oauth2_issuer_url,
        )

        # Check token type
        if payload.get("type") != token_type:
            return None

        # Validate required claims
        required_claims = ["sub", "exp", "iat", "jti"]
        if not all(claim in payload for claim in required_claims):
            return None

        return payload

    except JWTError:
        # Relaxed path: decode without issuer check, then validate against allowed aliases
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                audience="sandbox-platform",
                options={"verify_iss": False},
            )
            iss = payload.get("iss")
            if not iss or iss not in _issuer_aliases(settings.oauth2_issuer_url):
                return None
        except JWTError:
            return None


def generate_client_id() -> str:
    """Generate OAuth2 client ID."""
    import secrets

    return f"client_{secrets.token_urlsafe(16)}"


def generate_client_secret() -> str:
    """Generate OAuth2 client secret."""
    import secrets

    return secrets.token_urlsafe(32)
