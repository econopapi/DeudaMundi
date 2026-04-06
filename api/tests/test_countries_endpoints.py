from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_country_history_endpoint_returns_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def fake_get_country_history(*, db, iso3: str):  # type: ignore[no-untyped-def]
        return {
            "iso3": iso3.upper(),
            "items": [
                {
                    "year": 2024,
                    "total_external_debt_usd": 123.0,
                    "debt_per_capita_usd": None,
                    "debt_pct_gdp": None,
                    "gdp_usd": None,
                    "source": "worldbank",
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_country_history",
        fake_get_country_history,
    )

    response = client.get("/api/v1/countries/arg/history")

    assert response.status_code == 200
    assert response.json()["iso3"] == "ARG"
    assert response.json()["items"][0]["year"] == 2024


def test_country_history_endpoint_returns_404(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_country_history",
        lambda **kwargs: None,
    )

    response = client.get("/api/v1/countries/zzz/history")

    assert response.status_code == 404


def test_country_governments_endpoint_returns_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def fake_get_country_governments(*, db, iso3: str):  # type: ignore[no-untyped-def]
        return {
            "iso3": iso3.upper(),
            "items": [
                {
                    "leader_name": "Demo Leader",
                    "party": "Demo Party",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "political_lean": "center",
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_country_governments",
        fake_get_country_governments,
    )

    response = client.get("/api/v1/countries/arg/governments")

    assert response.status_code == 200
    assert response.json()["iso3"] == "ARG"
    assert response.json()["items"][0]["leader_name"] == "Demo Leader"


def test_country_governments_endpoint_returns_404(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_country_governments",
        lambda **kwargs: None,
    )

    response = client.get("/api/v1/countries/zzz/governments")

    assert response.status_code == 404
