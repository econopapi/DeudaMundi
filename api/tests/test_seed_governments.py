from app.etl.seed_governments import PILOT_GOVERNMENTS


def test_pilot_governments_contains_expected_countries() -> None:
    iso3_set = {row.iso3 for row in PILOT_GOVERNMENTS}

    assert {"ARG", "USA", "BRA", "DEU", "GRC"}.issubset(iso3_set)
    assert len(PILOT_GOVERNMENTS) >= 20
