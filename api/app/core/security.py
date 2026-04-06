from __future__ import annotations

from app.core.config import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

_rate_limiter: Limiter | None = None
_rate_limiter_limit: int | None = None

_STRICT_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
_DOCS_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'none'"
)


def _request_client_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def get_rate_limiter(limit_per_minute: int) -> Limiter:
    global _rate_limiter, _rate_limiter_limit
    if _rate_limiter is None or _rate_limiter_limit != limit_per_minute:
        _rate_limiter = Limiter(
            key_func=_request_client_key,
            default_limits=[f"{limit_per_minute}/minute"],
        )
        _rate_limiter_limit = limit_per_minute
    return _rate_limiter


def _rate_limit_exceeded_handler(_: Request, __: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"},
    )


def _content_security_policy_for_path(path: str) -> str:
    if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
        return _DOCS_CSP
    return _STRICT_CSP


def setup_security(app: FastAPI) -> None:
    limiter = get_rate_limiter(settings.rate_limit_requests_per_minute)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def apply_security(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = _content_security_policy_for_path(
            request.url.path
        )

        if settings.security_hsts_enabled:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
