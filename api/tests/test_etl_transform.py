from app.etl.transform import (
    latest_population_by_iso3,
    normalize_countries,
    normalize_debt_records,
    normalize_indicator_rows,
)


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
    raw_debt = [
        {"countryiso3code": "ARG", "date": "2023", "value": 280000000000},
        {"countryiso3code": "ARG", "date": "2022", "value": None},
        {"countryiso3code": "", "date": "2021", "value": 10},
    ]
    gdp_by_country_year = {("ARG", 2023): 560000000000.0}
    population_by_country_year = {("ARG", 2023): 46000000.0}

    records = normalize_debt_records(
        raw_debt,
        gdp_by_country_year=gdp_by_country_year,
        population_by_country_year=population_by_country_year,
    )

    assert len(records) == 1
    assert records[0].iso3 == "ARG"
    assert records[0].year == 2023
    assert records[0].total_external_debt_usd == 280000000000.0
    assert records[0].gdp_usd == 560000000000.0
    assert round(records[0].debt_pct_gdp or 0, 2) == 50.0
    assert round(records[0].debt_per_capita_usd or 0, 2) == 6086.96


def test_normalize_indicator_rows_and_latest_population() -> None:
    raw_population = [
        {"countryiso3code": "ARG", "date": "2022", "value": 45500000},
        {"countryiso3code": "ARG", "date": "2024", "value": 46000000},
        {"countryiso3code": "USA", "date": "2024", "value": 341000000},
        {"countryiso3code": "USA", "date": "bad-year", "value": 99},
    ]

    indicator = normalize_indicator_rows(raw_population)
    latest_population = latest_population_by_iso3(indicator)

    assert indicator[("ARG", 2024)] == 46000000.0
    assert latest_population["ARG"] == 46000000
    assert latest_population["USA"] == 341000000
