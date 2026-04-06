import app.core.security as security_module
from app.core.config import settings
from app.main import app
from fastapi.testclient import TestClient


def test_security_headers_are_present() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "Content-Security-Policy" in response.headers
    assert response.headers["Content-Security-Policy"] == (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    )


def test_docs_csp_allows_swagger_assets() -> None:
    with TestClient(app) as client:
        response = client.get("/docs")

    assert response.status_code == 200
    csp = response.headers["Content-Security-Policy"]
    assert "https://cdn.jsdelivr.net" in csp
    assert "script-src" in csp
    assert "style-src" in csp


def test_rate_limit_blocks_excess_requests() -> None:
    security_module._rate_limiter = None
    security_module._rate_limiter_limit = None
    app.state.limiter = security_module.get_rate_limiter(limit_per_minute=1)

    try:
        with TestClient(app) as client:
            headers = {"X-Forwarded-For": "203.0.113.10"}
            first = client.get("/api/v1/health", headers=headers)
            second = client.get("/api/v1/health", headers=headers)

        assert first.status_code == 200
        assert second.status_code == 429
        assert second.json()["detail"] == "Rate limit exceeded"
    finally:
        security_module._rate_limiter = None
        security_module._rate_limiter_limit = None
        app.state.limiter = security_module.get_rate_limiter(
            limit_per_minute=settings.rate_limit_requests_per_minute
        )
