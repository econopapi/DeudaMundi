import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def _disable_cache(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_cache_json",
        lambda key: None,
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.set_cache_json",
        lambda **kwargs: None,
    )


def test_list_countries_endpoint_returns_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def fake_list_countries(*, db, page: int, page_size: int, region):  # type: ignore[no-untyped-def]
        return {
            "page": page,
            "page_size": page_size,
            "total": 1,
            "items": [
                {
                    "iso3": "ARG",
                    "iso2": "AR",
                    "name_es": "Argentina",
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
        "app.api.v1.endpoints.countries.list_countries",
        fake_list_countries,
    )

    response = client.get("/api/v1/countries?page=1&page_size=20")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["iso3"] == "ARG"


def test_list_countries_endpoint_uses_cache_when_available(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_cache_json",
        lambda key: {
            "page": 1,
            "page_size": 20,
            "total": 1,
            "items": [
                {
                    "iso3": "USA",
                    "iso2": "US",
                    "name_es": "Estados Unidos",
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
        "app.api.v1.endpoints.countries.list_countries",
        fail_if_called,
    )

    response = client.get("/api/v1/countries")

    assert response.status_code == 200
    assert response.json()["items"][0]["iso3"] == "USA"


def test_country_detail_endpoint_returns_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def fake_get_country_detail(*, db, iso3: str):  # type: ignore[no-untyped-def]
        return {
            "iso3": iso3.upper(),
            "iso2": "AR",
            "name_es": "Argentina",
            "name_en": "Argentina",
            "region": "Latin America & Caribbean",
            "subregion": "South America",
            "population": 46000000,
            "capital": "Buenos Aires",
            "latest_year": 2024,
            "total_external_debt_usd": 123.0,
            "debt_per_capita_usd": 3.0,
            "debt_pct_gdp": 40.0,
            "gdp_usd": 500.0,
            "equivalences": [],
        }

    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_country_detail",
        fake_get_country_detail,
    )

    response = client.get("/api/v1/countries/arg")

    assert response.status_code == 200
    assert response.json()["iso3"] == "ARG"


def test_country_detail_endpoint_uses_cache_when_available(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_cache_json",
        lambda key: {
            "iso3": "USA",
            "iso2": "US",
            "name_es": "Estados Unidos",
            "name_en": "United States",
            "region": "North America",
            "subregion": "North America",
            "population": 340000000,
            "capital": "Washington, D.C.",
            "latest_year": 2024,
            "total_external_debt_usd": 999.0,
            "debt_per_capita_usd": 10.0,
            "debt_pct_gdp": 90.0,
            "gdp_usd": 2000.0,
            "equivalences": [],
        },
    )

    def fail_if_called(**kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("service should not run when cache hit exists")

    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_country_detail",
        fail_if_called,
    )

    response = client.get("/api/v1/countries/usa")

    assert response.status_code == 200
    assert response.json()["iso3"] == "USA"


def test_country_detail_endpoint_returns_404(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_country_detail",
        lambda **kwargs: None,
    )

    response = client.get("/api/v1/countries/zzz")

    assert response.status_code == 404


def test_compare_countries_endpoint_returns_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_countries_compare",
        lambda **kwargs: {
            "requested_iso3": ["ARG", "USA"],
            "missing_iso3": [],
            "item_count": 2,
            "items": [
                {
                    "detail": {
                        "iso3": "ARG",
                        "iso2": "AR",
                        "name_es": "Argentina",
                        "name_en": "Argentina",
                        "region": "Latin America & Caribbean",
                        "subregion": "South America",
                        "population": 46000000,
                        "capital": "Buenos Aires",
                        "latest_year": 2024,
                        "total_external_debt_usd": 123.0,
                        "debt_per_capita_usd": 3.0,
                        "debt_pct_gdp": 40.0,
                        "gdp_usd": 500.0,
                        "equivalences": [],
                    },
                    "history": [],
                },
                {
                    "detail": {
                        "iso3": "USA",
                        "iso2": "US",
                        "name_es": "Estados Unidos",
                        "name_en": "United States",
                        "region": "North America",
                        "subregion": "North America",
                        "population": 340000000,
                        "capital": "Washington, D.C.",
                        "latest_year": 2024,
                        "total_external_debt_usd": 999.0,
                        "debt_per_capita_usd": 10.0,
                        "debt_pct_gdp": 90.0,
                        "gdp_usd": 2000.0,
                        "equivalences": [],
                    },
                    "history": [],
                },
            ],
        },
    )

    response = client.get("/api/v1/countries/compare?iso3=arg&iso3=usa")

    assert response.status_code == 200
    payload = response.json()
    assert payload["item_count"] == 2
    assert payload["items"][0]["detail"]["iso3"] == "ARG"


def test_compare_countries_endpoint_uses_cache_when_available(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_cache_json",
        lambda key: {
            "requested_iso3": ["ARG", "USA"],
            "missing_iso3": [],
            "item_count": 2,
            "items": [
                {
                    "detail": {
                        "iso3": "ARG",
                        "iso2": "AR",
                        "name_es": "Argentina",
                        "name_en": "Argentina",
                        "region": "Latin America & Caribbean",
                        "subregion": "South America",
                        "population": 46000000,
                        "capital": "Buenos Aires",
                        "latest_year": 2024,
                        "total_external_debt_usd": 123.0,
                        "debt_per_capita_usd": 3.0,
                        "debt_pct_gdp": 40.0,
                        "gdp_usd": 500.0,
                        "equivalences": [],
                    },
                    "history": [],
                },
                {
                    "detail": {
                        "iso3": "USA",
                        "iso2": "US",
                        "name_es": "Estados Unidos",
                        "name_en": "United States",
                        "region": "North America",
                        "subregion": "North America",
                        "population": 340000000,
                        "capital": "Washington, D.C.",
                        "latest_year": 2024,
                        "total_external_debt_usd": 999.0,
                        "debt_per_capita_usd": 10.0,
                        "debt_pct_gdp": 90.0,
                        "gdp_usd": 2000.0,
                        "equivalences": [],
                    },
                    "history": [],
                },
            ],
        },
    )

    def fail_if_called(**kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("service should not run when cache hit exists")

    monkeypatch.setattr(
        "app.api.v1.endpoints.countries.get_countries_compare",
        fail_if_called,
    )

    response = client.get("/api/v1/countries/compare?iso3=arg&iso3=usa")

    assert response.status_code == 200
    assert response.json()["item_count"] == 2


def test_compare_countries_endpoint_requires_two_iso3() -> None:
    response = client.get("/api/v1/countries/compare?iso3=arg")

    assert response.status_code == 422


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
