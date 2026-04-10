from datetime import date

from app.etl.governments_wikidata_client import (
    WikidataGovernmentPeriod,
    WikidataGovernmentsClient,
    select_preferred_role_periods,
)


def test_select_preferred_role_periods_prefers_p6_when_timeline_is_available() -> None:
    periods = [
        WikidataGovernmentPeriod("DEU", "A", date(2000, 1, 1), date(2005, 1, 1), "p6"),
        WikidataGovernmentPeriod("DEU", "B", date(2005, 1, 1), None, "p6"),
        WikidataGovernmentPeriod("DEU", "X", date(2001, 1, 1), date(2006, 1, 1), "p35"),
        WikidataGovernmentPeriod("DEU", "Y", date(2006, 1, 1), None, "p35"),
    ]

    selected = select_preferred_role_periods(periods)

    assert len(selected) == 2
    assert {row.role for row in selected} == {"p6"}


def test_select_preferred_role_periods_falls_back_to_p35_when_p6_is_sparse() -> None:
    periods = [
        WikidataGovernmentPeriod("USA", "Only One", date(2021, 1, 20), None, "p6"),
        WikidataGovernmentPeriod("USA", "Older", date(2009, 1, 20), date(2017, 1, 20), "p35"),
        WikidataGovernmentPeriod("USA", "Newer", date(2017, 1, 20), None, "p35"),
    ]

    selected = select_preferred_role_periods(periods)

    assert len(selected) == 2
    assert {row.role for row in selected} == {"p35"}


def test_build_query_and_parse_payload() -> None:
    client = WikidataGovernmentsClient(timeout_seconds=5.0, chunk_size=2)
    query = client._build_query(["ARG", "USA"], min_start_year=1990)

    assert "VALUES ?iso3 { \"ARG\" \"USA\" }" in query
    assert "?country p:P6 ?statement" in query
    assert "?country p:P35 ?statement" in query
    assert "FILTER(YEAR(?start) >= 1990)" in query

    payload = {
        "results": {
            "bindings": [
                {
                    "iso3": {"value": "ARG"},
                    "leaderLabel": {"value": "Leader One"},
                    "start": {"value": "2019-12-10T00:00:00Z"},
                    "end": {"value": "2023-12-10T00:00:00Z"},
                    "role": {"value": "p35"},
                },
                {
                    "iso3": {"value": "ARG"},
                    "leaderLabel": {"value": "Leader Two"},
                    "start": {"value": "2023-12-10T00:00:00Z"},
                    "role": {"value": "p35"},
                },
                {
                    "iso3": {"value": "INVALID"},
                    "leaderLabel": {"value": "Bad"},
                    "start": {"value": "2023-12-10T00:00:00Z"},
                    "role": {"value": "p35"},
                },
            ]
        }
    }

    rows = client._parse_payload(payload)

    assert len(rows) == 2
    assert rows[0].iso3 == "ARG"
    assert rows[0].start_date == date(2019, 12, 10)


def test_fetch_periods_respects_max_duration(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    client = WikidataGovernmentsClient(timeout_seconds=5.0, chunk_size=1, max_duration_seconds=10.0)

    class FakeResponse:
        def raise_for_status(self) -> None:
            return

        def json(self) -> dict:
            return {"results": {"bindings": []}}

    class FakeHttpClient:
        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore[no-untyped-def]
            return False

        def get(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return FakeResponse()

    elapsed_points = iter([0.0, 11.0])
    monkeypatch.setattr("app.etl.governments_wikidata_client.perf_counter", lambda: next(elapsed_points))
    monkeypatch.setattr("app.etl.governments_wikidata_client.httpx.Client", FakeHttpClient)

    try:
        client.fetch_periods({"ARG", "USA"}, min_start_year=1990)
        assert False, "Expected TimeoutError"
    except TimeoutError:
        assert True
