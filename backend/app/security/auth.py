"""Verify Supabase access tokens for protected SentinelAI API routes."""
from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient, PyJWTError

from app.config import get_settings


@dataclass(frozen=True)
class CurrentUser:
    id: str


bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache(maxsize=8)
def get_jwks_client(jwks_url: str) -> PyJWKClient:
    """Cache the Supabase public-key client."""
    return PyJWKClient(jwks_url, cache_keys=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    """Require a valid Supabase access token."""
    unauthorized = HTTPException(
        status_code=401,
        detail="Valid authentication token required",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    settings = get_settings()
    issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1"

    try:
        token = credentials.credentials
        algorithm = jwt.get_unverified_header(token).get("alg")
        if algorithm == "ES256":
            jwks_url = f"{issuer}/.well-known/jwks.json"
            signing_key = get_jwks_client(jwks_url).get_signing_key_from_jwt(token)
            key = signing_key.key
        elif algorithm == "HS256" and settings.supabase_jwt_secret:
            key = settings.supabase_jwt_secret
        else:
            raise unauthorized

        payload = jwt.decode(
            token,
            key,
            algorithms=[algorithm],
            audience="authenticated",
            issuer=issuer,
        )
    except (PyJWTError, jwt.PyJWKClientError, jwt.PyJWKClientConnectionError) as exc:
        raise unauthorized from exc

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise unauthorized

    return CurrentUser(id=user_id)
