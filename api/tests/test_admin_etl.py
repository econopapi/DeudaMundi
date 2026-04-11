from app.core.config import settings
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_admin_etl_requires_api_key() -> None:
    original_key = settings.admin_api_key
    settings.admin_api_key = "test-secret"

    try:
        response = client.post("/api/v1/admin/etl/world-bank/run")
        assert response.status_code == 401
    finally:
        settings.admin_api_key = original_key


def test_admin_etl_runs_when_key_is_valid(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    original_key = settings.admin_api_key
    settings.admin_api_key = "test-secret"

    def fake_run_world_bank_etl() -> dict[str, int]:
        return {
            "countries_processed": 2,
            "debt_records_processed": 10,
            "debt_records_upserted": 8,
        }

    monkeypatch.setattr("app.api.v1.endpoints.admin.run_world_bank_etl", fake_run_world_bank_etl)

    try:
        response = client.post(
            "/api/v1/admin/etl/world-bank/run",
            headers={"X-API-Key": "test-secret"},
        )
        assert response.status_code == 200
        assert response.json()["debt_records_upserted"] == 8

        global_response = client.post(
            "/api/v1/admin/etl/run",
            headers={"X-API-Key": "test-secret"},
        )
        assert global_response.status_code == 200
        assert global_response.json()["debt_records_upserted"] == 8
    finally:
        settings.admin_api_key = original_key


def test_admin_governments_etl_runs_with_source_override(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    original_key = settings.admin_api_key
    settings.admin_api_key = "test-secret"

    calls: list[str | None] = []

    def fake_seed_governments(source: str | None = None) -> dict[str, int | str]:
        calls.append(source)
        return {
            "seed_source": source or "hybrid",
            "rows_prepared": 3,
            "rows_seed_input": 4,
            "missing_countries": 0,
            "countries_requested": 2,
        }

    monkeypatch.setattr("app.api.v1.endpoints.admin.seed_governments", fake_seed_governments)

    try:
        response = client.post(
            "/api/v1/admin/etl/governments/run?source=pilot",
            headers={"X-API-Key": "test-secret"},
        )
        assert response.status_code == 200
        assert response.json()["seed_source"] == "pilot"
        assert calls == ["pilot"]
    finally:
        settings.admin_api_key = original_key
