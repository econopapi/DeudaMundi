from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_rankings_endpoint_returns_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.rankings.get_cache_json",
        lambda key: None,
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.rankings.set_cache_json",
        lambda **kwargs: None,
    )

    def fake_get_rankings(*, db, metric: str, region, limit: int):  # type: ignore[no-untyped-def]
        return {
            "metric": metric,
            "region": region,
            "limit": limit,
            "items": [
                {
                    "rank": 1,
                    "iso3": "ARG",
                    "name_en": "Argentina",
                    "region": "Latin America & Caribbean",
                    "value": 123.0,
                    "latest_year": 2024,
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.v1.endpoints.rankings.get_rankings",
        fake_get_rankings,
    )

    response = client.get("/api/v1/rankings?metric=absolute&limit=10")

    assert response.status_code == 200
    assert response.json()["metric"] == "absolute"
    assert response.json()["items"][0]["iso3"] == "ARG"


def test_rankings_endpoint_uses_cache_when_available(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.rankings.get_cache_json",
        lambda key: {
            "metric": "absolute",
            "region": None,
            "limit": 20,
            "items": [
                {
                    "rank": 1,
                    "iso3": "USA",
                    "name_en": "United States",
                    "region": "North America",
                    "value": 999.0,
                    "latest_year": 2024,
                }
            ],
        },
    )

    def fail_if_called(**kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("service should not run when cache hit exists")

    monkeypatch.setattr(
        "app.api.v1.endpoints.rankings.get_rankings",
        fail_if_called,
    )

    response = client.get("/api/v1/rankings")

    assert response.status_code == 200
    assert response.json()["items"][0]["iso3"] == "USA"


def test_rankings_endpoint_returns_422_on_invalid_metric(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.rankings.get_cache_json",
        lambda key: None,
    )

    def raise_invalid_metric(**kwargs):  # type: ignore[no-untyped-def]
        raise ValueError("Invalid metric 'foo'")

    monkeypatch.setattr(
        "app.api.v1.endpoints.rankings.get_rankings",
        raise_invalid_metric,
    )

    response = client.get("/api/v1/rankings?metric=foo")

    assert response.status_code == 422
