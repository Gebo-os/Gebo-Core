"""Auth JWT middleware — Supabase + Firebase (optional production gate)."""
from __future__ import annotations

import logging
import os
from typing import Any

import jwt
from jwt import PyJWKClient
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

FIREBASE_JWKS_URL = (
    "https://www.googleapis.com/service_accounts/v1/jwk/"
    "securetoken@system.gserviceaccount.com"
)

PUBLIC_PATHS = frozenset({
    "/health",
    "/status",
    "/integrate/bootstrap",
    "/system/production-readiness",
    "/system/v1-readiness",
    "/system/modules",
    "/v1/security/verify-turnstile",
    "/v1/billing/plans",
    "/v1/identity/owner-status",
})

_firebase_jwk_client: PyJWKClient | None = None
_supabase_jwk_client: PyJWKClient | None = None


def release_mode() -> str:
    return os.getenv("GEBO_RELEASE_MODE", "owner").lower()


def auth_enabled() -> bool:
    if release_mode() != "production":
        return False
    return os.getenv("GEBO_AUTH_ENABLED", "false").lower() in ("1", "true", "yes")


def firebase_project_id() -> str:
    return os.getenv("FIREBASE_PROJECT_ID", "").strip()


def supabase_url() -> str:
    return os.getenv("SUPABASE_URL", "").strip().rstrip("/")


def supabase_jwt_secret() -> str:
    return os.getenv("SUPABASE_JWT_SECRET", "").strip()


def supabase_jwks_url() -> str:
    explicit = os.getenv("SUPABASE_JWKS_URL", "").strip()
    if explicit:
        return explicit
    base = supabase_url()
    if base:
        return f"{base}/auth/v1/.well-known/jwks.json"
    return ""


def firebase_auth_configured() -> bool:
    return bool(firebase_project_id())


def supabase_auth_configured() -> bool:
    return bool(supabase_jwt_secret() or supabase_jwks_url())


def auth_providers() -> list[str]:
    providers: list[str] = []
    if supabase_auth_configured():
        providers.append("supabase")
    if firebase_auth_configured():
        providers.append("firebase")
    return providers


def _get_firebase_jwk_client() -> PyJWKClient:
    global _firebase_jwk_client
    if _firebase_jwk_client is None:
        _firebase_jwk_client = PyJWKClient(FIREBASE_JWKS_URL, cache_keys=True)
    return _firebase_jwk_client


def _get_supabase_jwk_client() -> PyJWKClient | None:
    global _supabase_jwk_client
    url = supabase_jwks_url()
    if not url:
        return None
    if _supabase_jwk_client is None:
        _supabase_jwk_client = PyJWKClient(url, cache_keys=True)
    return _supabase_jwk_client


def verify_firebase_token(token: str) -> dict[str, Any]:
    project_id = firebase_project_id()
    if not project_id:
        raise ValueError("FIREBASE_PROJECT_ID not configured")
    client = _get_firebase_jwk_client()
    signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=project_id,
        issuer=f"https://securetoken.google.com/{project_id}",
    )


def verify_supabase_token(token: str) -> dict[str, Any]:
    secret = supabase_jwt_secret()
    if secret:
        return jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
        )

    jwks_client = _get_supabase_jwk_client()
    if jwks_client is None:
        raise ValueError("Supabase auth not configured")

    signing_key = jwks_client.get_signing_key_from_jwt(token)
    issuer = f"{supabase_url()}/auth/v1" if supabase_url() else None
    options: dict[str, Any] = {"verify_aud": False}
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        issuer=issuer,
        options=options,
    )


def verify_token(token: str) -> tuple[dict[str, Any], str]:
    """Verify JWT — Supabase first when configured, then Firebase."""
    errors: list[str] = []

    if supabase_auth_configured():
        try:
            return verify_supabase_token(token), "supabase"
        except Exception as exc:
            errors.append(f"supabase: {exc}")

    if firebase_auth_configured():
        try:
            return verify_firebase_token(token), "firebase"
        except Exception as exc:
            errors.append(f"firebase: {exc}")

    if not errors:
        raise ValueError("No auth provider configured")
    raise ValueError("; ".join(errors))


def is_protected_route(path: str, method: str) -> bool:
    if not auth_enabled():
        return False
    if path in PUBLIC_PATHS:
        return False
    upper = method.upper()
    if path == "/chat" and upper == "POST":
        return True
    if path.startswith("/actions"):
        return True
    if path == "/memory" and upper == "POST":
        return True
    if path == "/system/build" and upper == "POST":
        return True
    return False


async def auth_middleware(request: Request, call_next):
    if not is_protected_route(request.url.path, request.method):
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing Bearer token"},
        )

    token = auth_header[7:].strip()
    if not token:
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing Bearer token"},
        )

    try:
        payload, provider = verify_token(token)
        request.state.auth_provider = provider
        request.state.user_id = payload.get("sub")
        if provider == "firebase":
            request.state.firebase_uid = payload.get("sub")
            request.state.firebase_token = payload
        elif provider == "supabase":
            request.state.supabase_uid = payload.get("sub")
            request.state.supabase_token = payload
    except Exception as exc:
        logger.debug("JWT verification failed: %s", exc)
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired token"},
        )

    return await call_next(request)
