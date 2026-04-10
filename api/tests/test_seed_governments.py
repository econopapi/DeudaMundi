from datetime import date

from app.etl.seed_governments import (
    PILOT_GOVERNMENTS,
    GovernmentSeed,
    _merge_wikidata_with_pilot,
    seed_governments,
)


def test_pilot_governments_contains_expected_countries() -> None:
    iso3_set = {row.iso3 for row in PILOT_GOVERNMENTS}

    assert {"ARG", "USA", "BRA", "DEU", "GRC"}.issubset(iso3_set)
    assert len(PILOT_GOVERNMENTS) >= 20


def test_merge_wikidata_with_pilot_enriches_optional_fields() -> None:
    wikidata_rows = [
        GovernmentSeed(
            iso3="ARG",
            leader_name="Mauricio Macri",
            party=None,
            start_date=date(2015, 12, 10),
            end_date=date(2019, 12, 10),
            political_lean=None,
        )
    ]

    merged = _merge_wikidata_with_pilot(wikidata_rows)
    merged_map = {(row.iso3, row.leader_name, row.start_date): row for row in merged}

    enriched = merged_map[("ARG", "Mauricio Macri", date(2015, 12, 10))]
    assert enriched.party == "PRO"
    assert enriched.political_lean == "center-right"


def test_seed_governments_uses_injected_session(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    captured: dict[str, object] = {}

    def fake_seed_with_session(db, mode):  # type: ignore[no-untyped-def]
        captured["db"] = db
        captured["mode"] = mode
        return {"seed_source": "pilot", "rows_prepared": 22}

    def fail_begin():  # type: ignore[no-untyped-def]
        raise AssertionError("SessionLocal.begin should not be called when db is provided")

    monkeypatch.setattr("app.etl.seed_governments._seed_governments_with_session", fake_seed_with_session)
    monkeypatch.setattr("app.etl.seed_governments.SessionLocal.begin", fail_begin)

    fake_db = object()
    result = seed_governments(source="pilot", db=fake_db)

    assert captured["db"] is fake_db
    assert captured["mode"] == "pilot"
    assert result["seed_source"] == "pilot"
