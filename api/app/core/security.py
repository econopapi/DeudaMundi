from __future__ import annotations

import threading
import time

from app.core.config import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

_WINDOW_SECONDS = 60


class InMemoryRateLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        self.limit_per_minute = limit_per_minute
        self._lock = threading.Lock()
        self._windows: dict[str, tuple[int, float]] = {}

    def allow(self, key: str) -> tuple[bool, int | None]:
        now = time.time()

        with self._lock:
            current_count, started_at = self._windows.get(key, (0, now))
            elapsed = now - started_at

            if elapsed >= _WINDOW_SECONDS:
                self._windows[key] = (1, now)
                return True, None

            if current_count >= self.limit_per_minute:
                retry_after = max(1, int(_WINDOW_SECONDS - elapsed))
                return False, retry_after

            self._windows[key] = (current_count + 1, started_at)
            return True, None


_rate_limiter: InMemoryRateLimiter | None = None


def get_rate_limiter(limit_per_minute: int) -> InMemoryRateLimiter:
    global _rate_limiter
    if _rate_limiter is None or _rate_limiter.limit_per_minute != limit_per_minute:
        _rate_limiter = InMemoryRateLimiter(limit_per_minute=limit_per_minute)
    return _rate_limiter


def _request_client_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def setup_security(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def apply_security(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        limiter = get_rate_limiter(settings.rate_limit_requests_per_minute)
        allowed, retry_after = limiter.allow(_request_client_key(request))
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(retry_after or 1)},
            )

        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )

        if settings.security_hsts_enabled:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
