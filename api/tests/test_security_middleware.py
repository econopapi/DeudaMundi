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


def test_rate_limit_blocks_excess_requests() -> None:
    original_limit = settings.rate_limit_requests_per_minute
    settings.rate_limit_requests_per_minute = 1
    security_module._rate_limiter = None

    try:
        with TestClient(app) as client:
            first = client.get("/api/v1/health")
            second = client.get("/api/v1/health")

        assert first.status_code == 200
        assert second.status_code == 429
        assert second.json()["detail"] == "Rate limit exceeded"
    finally:
        settings.rate_limit_requests_per_minute = original_limit
        security_module._rate_limiter = None
