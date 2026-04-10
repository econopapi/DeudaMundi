from app.etl.transform import (
    keep_imf_proxy_for_uncovered_countries,
    latest_population_by_iso3,
    merge_debt_records_by_priority,
    normalize_countries,
    normalize_debt_records,
    normalize_imf_debt_records,
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
    external_debt_by_country_year = {("ARG", 2023): 280000000000.0}
    gdp_by_country_year = {("ARG", 2023): 560000000000.0, ("ARG", 2022): 500000000000.0}
    population_by_country_year = {("ARG", 2023): 46000000.0}

    records = normalize_debt_records(
        external_debt_by_country_year=external_debt_by_country_year,
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
    assert records[0].debt_concept == "external_debt_bop"
    assert records[0].data_source == "World Bank IDS DT.DOD.DECT.CD"
    assert records[0].source == "wb_ids_dt_dod_dect_cd"


def test_normalize_debt_records_avoids_public_debt_proxy_for_usa_like_cases() -> None:
    gdp_by_country_year = {("USA", 2024): 29000000000000.0}
    population_by_country_year = {("USA", 2024): 340000000.0}
    external_debt_by_country_year = {}

    records = normalize_debt_records(
        external_debt_by_country_year=external_debt_by_country_year,
        gdp_by_country_year=gdp_by_country_year,
        population_by_country_year=population_by_country_year,
    )

    assert records == []


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


def test_normalize_imf_debt_records_builds_stock_from_ratio_and_gdp() -> None:
    debt_pct_gdp_by_country_year = {("USA", 2024): 120.0}
    gdp_by_country_year = {("USA", 2024): 28000000000000.0}
    population_by_country_year = {("USA", 2024): 340000000.0}

    records = normalize_imf_debt_records(
        debt_pct_gdp_by_country_year=debt_pct_gdp_by_country_year,
        gdp_by_country_year=gdp_by_country_year,
        population_by_country_year=population_by_country_year,
    )

    assert len(records) == 1
    assert records[0].iso3 == "USA"
    assert records[0].year == 2024
    assert records[0].total_external_debt_usd == 33600000000000.0
    assert records[0].gdp_usd == 28000000000000.0
    assert records[0].debt_pct_gdp == 120.0
    assert records[0].debt_concept == "public_debt_proxy"
    assert records[0].source == "imf_dm_proxy_ggxwdg"


def test_normalize_imf_debt_records_uses_latest_population_fallback() -> None:
    debt_pct_gdp_by_country_year = {("USA", 2026): 100.0}
    gdp_by_country_year = {("USA", 2026): 30000000000000.0}
    population_by_country_year = {("USA", 2024): 340000000.0}

    records = normalize_imf_debt_records(
        debt_pct_gdp_by_country_year=debt_pct_gdp_by_country_year,
        gdp_by_country_year=gdp_by_country_year,
        population_by_country_year=population_by_country_year,
    )

    assert len(records) == 1
    assert records[0].debt_per_capita_usd is not None
    assert round(records[0].debt_per_capita_usd or 0, 2) == 88235.29


def test_merge_debt_records_by_priority_prefers_world_bank_over_imf() -> None:
    wb_record = normalize_debt_records(
        external_debt_by_country_year={("ARG", 2024): 300000000000.0},
        gdp_by_country_year={("ARG", 2024): 600000000000.0},
        population_by_country_year={("ARG", 2024): 46000000.0},
    )[0]

    imf_record = normalize_imf_debt_records(
        debt_pct_gdp_by_country_year={("ARG", 2024): 100.0},
        gdp_by_country_year={("ARG", 2024): 700000000000.0},
        population_by_country_year={("ARG", 2024): 46000000.0},
    )[0]

    merged = merge_debt_records_by_priority([imf_record, wb_record])

    assert len(merged) == 1
    assert merged[0].source == "wb_ids_dt_dod_dect_cd"
    assert merged[0].debt_concept == "external_debt_bop"


def test_keep_imf_proxy_for_uncovered_countries_filters_wb_covered_iso3() -> None:
    world_bank_rows = normalize_debt_records(
        external_debt_by_country_year={("ARG", 2024): 300000000000.0},
        gdp_by_country_year={("ARG", 2024): 600000000000.0},
        population_by_country_year={("ARG", 2024): 46000000.0},
    )

    imf_rows = normalize_imf_debt_records(
        debt_pct_gdp_by_country_year={
            ("ARG", 2024): 110.0,
            ("USA", 2024): 120.0,
        },
        gdp_by_country_year={
            ("ARG", 2024): 700000000000.0,
            ("USA", 2024): 28000000000000.0,
        },
        population_by_country_year={
            ("ARG", 2024): 46000000.0,
            ("USA", 2024): 340000000.0,
        },
    )

    filtered_imf_rows, dropped = keep_imf_proxy_for_uncovered_countries(
        world_bank_rows=world_bank_rows,
        imf_rows=imf_rows,
    )

    assert dropped == 1
    assert len(filtered_imf_rows) == 1
    assert filtered_imf_rows[0].iso3 == "USA"
