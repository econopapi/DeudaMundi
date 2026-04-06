from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_globe_data_endpoint_returns_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.globe_data.get_cache_json",
        lambda key: None,
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.globe_data.set_cache_json",
        lambda **kwargs: None,
    )

    def fake_get_globe_data(*, db, region):  # type: ignore[no-untyped-def]
        return {
            "item_count": 1,
            "items": [
                {
                    "iso3": "ARG",
                    "name_en": "Argentina",
                    "region": "Latin America & Caribbean",
                    "latest_year": 2024,
                    "total_external_debt_usd": 123.0,
                    "debt_per_capita_usd": 3.0,
                    "debt_pct_gdp": 40.0,
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.v1.endpoints.globe_data.get_globe_data",
        fake_get_globe_data,
    )

    response = client.get("/api/v1/globe-data")

    assert response.status_code == 200
    payload = response.json()
    assert payload["item_count"] == 1
    assert payload["items"][0]["iso3"] == "ARG"


def test_globe_data_endpoint_uses_cache_when_available(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.globe_data.get_cache_json",
        lambda key: {
            "item_count": 1,
            "items": [
                {
                    "iso3": "USA",
                    "name_en": "United States",
                    "region": "North America",
                    "latest_year": 2024,
                    "total_external_debt_usd": 999.0,
                    "debt_per_capita_usd": 10.0,
                    "debt_pct_gdp": 90.0,
                }
            ],
        },
    )

    def fail_if_called(**kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("service should not run when cache hit exists")

    monkeypatch.setattr(
        "app.api.v1.endpoints.globe_data.get_globe_data",
        fail_if_called,
    )

    response = client.get("/api/v1/globe-data")

    assert response.status_code == 200
    assert response.json()["items"][0]["iso3"] == "USA"
