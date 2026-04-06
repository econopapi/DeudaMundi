from app.etl.transform import normalize_countries, normalize_debt_records


def test_normalize_countries_filters_aggregates() -> None:
    raw = [
        {
            "id": "ARG",
            "iso2Code": "AR",
            "name": "Argentina",
            "region": {"value": "Latin America & Caribbean"},
            "adminregion": {"value": "Latin America & Caribbean (excluding high income)"},
            "capitalCity": "Buenos Aires",
        },
        {
            "id": "WLD",
            "iso2Code": "1W",
            "name": "World",
            "region": {"value": "Aggregates"},
            "adminregion": {"value": ""},
            "capitalCity": "",
        },
    ]

    normalized = normalize_countries(raw)

    assert list(normalized.keys()) == ["ARG"]
    assert normalized["ARG"].iso2 == "AR"
    assert normalized["ARG"].capital == "Buenos Aires"


def test_normalize_debt_records_parses_only_valid_values() -> None:
    raw = [
        {"countryiso3code": "ARG", "date": "2023", "value": 280000000000},
        {"countryiso3code": "ARG", "date": "2022", "value": None},
        {"countryiso3code": "", "date": "2021", "value": 10},
    ]

    records = normalize_debt_records(raw)

    assert len(records) == 1
    assert records[0].iso3 == "ARG"
    assert records[0].year == 2023
    assert records[0].total_external_debt_usd == 280000000000.0
