from datetime import UTC, datetime

from app.etl.imf_client import ImfDataMapperClient


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class _FakeHttpxClient:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        return None

    def get(self, url: str) -> _FakeResponse:
        return _FakeResponse(self.payload)


def test_imf_client_parses_indicator_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    payload = {
        "values": {
            "GGXWDG_NGDP": {
                "USA": {"2024": 120.0, "bad-year": 80.0},
                "AA": {"2024": 50.0},
            }
        }
    }

    monkeypatch.setattr(
        "app.etl.imf_client.httpx.Client",
        lambda timeout: _FakeHttpxClient(payload),
    )

    client = ImfDataMapperClient()
    result = client.fetch_general_government_debt_to_gdp()

    assert result == {("USA", 2024): 120.0}


def test_imf_client_skips_future_years(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    next_year = datetime.now(tz=UTC).year + 1
    payload = {
        "values": {
            "NGDPD": {
                "JPN": {str(next_year): 5.0, "2024": 4.5},
            }
        }
    }

    monkeypatch.setattr(
        "app.etl.imf_client.httpx.Client",
        lambda timeout: _FakeHttpxClient(payload),
    )

    client = ImfDataMapperClient()
    result = client.fetch_nominal_gdp_usd_billions()

    assert ("JPN", next_year) not in result
    assert result[("JPN", 2024)] == 4.5
