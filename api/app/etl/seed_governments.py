from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.etl.governments_wikidata_client import WikidataGovernmentsClient
from app.models import Country, Government

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GovernmentSeed:
    iso3: str
    leader_name: str
    party: str | None
    start_date: date
    end_date: date | None
    political_lean: str | None


PILOT_GOVERNMENTS: tuple[GovernmentSeed, ...] = (
    GovernmentSeed(
        "ARG",
        "Néstor Kirchner",
        "Frente para la Victoria",
        date(2003, 5, 25),
        date(2007, 12, 10),
        "center-left",
    ),
    GovernmentSeed(
        "ARG",
        "Cristina Fernández de Kirchner",
        "Frente para la Victoria",
        date(2007, 12, 10),
        date(2015, 12, 10),
        "center-left",
    ),
    GovernmentSeed(
        "ARG",
        "Mauricio Macri",
        "PRO",
        date(2015, 12, 10),
        date(2019, 12, 10),
        "center-right",
    ),
    GovernmentSeed(
        "ARG",
        "Alberto Fernández",
        "Frente de Todos",
        date(2019, 12, 10),
        date(2023, 12, 10),
        "center-left",
    ),
    GovernmentSeed(
        "ARG",
        "Javier Milei",
        "La Libertad Avanza",
        date(2023, 12, 10),
        None,
        "right-libertarian",
    ),
    GovernmentSeed(
        "USA",
        "Barack Obama",
        "Democratic Party",
        date(2009, 1, 20),
        date(2017, 1, 20),
        "center-left",
    ),
    GovernmentSeed(
        "USA",
        "Donald Trump",
        "Republican Party",
        date(2017, 1, 20),
        date(2021, 1, 20),
        "right",
    ),
    GovernmentSeed(
        "USA",
        "Joe Biden",
        "Democratic Party",
        date(2021, 1, 20),
        date(2025, 1, 20),
        "center-left",
    ),
    GovernmentSeed(
        "USA",
        "Donald Trump",
        "Republican Party",
        date(2025, 1, 20),
        None,
        "right",
    ),
    GovernmentSeed(
        "BRA",
        "Luiz Inácio Lula da Silva",
        "PT",
        date(2003, 1, 1),
        date(2011, 1, 1),
        "left",
    ),
    GovernmentSeed("BRA", "Dilma Rousseff", "PT", date(2011, 1, 1), date(2016, 8, 31), "left"),
    GovernmentSeed("BRA", "Michel Temer", "MDB", date(2016, 8, 31), date(2019, 1, 1), "center"),
    GovernmentSeed("BRA", "Jair Bolsonaro", "PL", date(2019, 1, 1), date(2023, 1, 1), "right"),
    GovernmentSeed("BRA", "Luiz Inácio Lula da Silva", "PT", date(2023, 1, 1), None, "left"),
    GovernmentSeed(
        "DEU",
        "Gerhard Schröder",
        "SPD",
        date(1998, 10, 27),
        date(2005, 11, 22),
        "center-left",
    ),
    GovernmentSeed(
        "DEU",
        "Angela Merkel",
        "CDU",
        date(2005, 11, 22),
        date(2021, 12, 8),
        "center-right",
    ),
    GovernmentSeed("DEU", "Olaf Scholz", "SPD", date(2021, 12, 8), None, "center-left"),
    GovernmentSeed(
        "GRC",
        "Konstantinos Simitis",
        "PASOK",
        date(1996, 1, 18),
        date(2004, 3, 10),
        "center-left",
    ),
    GovernmentSeed(
        "GRC",
        "Kostas Karamanlis",
        "New Democracy",
        date(2004, 3, 10),
        date(2009, 10, 6),
        "center-right",
    ),
    GovernmentSeed(
        "GRC",
        "George Papandreou",
        "PASOK",
        date(2009, 10, 6),
        date(2011, 11, 11),
        "center-left",
    ),
    GovernmentSeed("GRC", "Alexis Tsipras", "SYRIZA", date(2015, 1, 26), date(2019, 7, 8), "left"),
    GovernmentSeed(
        "GRC",
        "Kyriakos Mitsotakis",
        "New Democracy",
        date(2019, 7, 8),
        None,
        "center-right",
    ),
)


def _merge_wikidata_with_pilot(wikidata_seeds: list[GovernmentSeed]) -> list[GovernmentSeed]:
    by_key: dict[tuple[str, str, date], GovernmentSeed] = {
        (seed.iso3, seed.leader_name, seed.start_date): seed
        for seed in wikidata_seeds
    }

    for pilot in PILOT_GOVERNMENTS:
        key = (pilot.iso3, pilot.leader_name, pilot.start_date)
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = pilot
            continue

        # Prefer richer pilot metadata if wikidata row lacks optional fields.
        by_key[key] = GovernmentSeed(
            iso3=existing.iso3,
            leader_name=existing.leader_name,
            party=existing.party or pilot.party,
            start_date=existing.start_date,
            end_date=existing.end_date,
            political_lean=existing.political_lean or pilot.political_lean,
        )

    return sorted(by_key.values(), key=lambda row: (row.iso3, row.start_date, row.leader_name))


def _resolve_seed_mode(source: str | None) -> str:
    mode = (source or settings.etl_governments_source or "hybrid").strip().lower()
    if mode not in {"pilot", "wikidata", "hybrid"}:
        raise ValueError("Invalid governments seed source. Use pilot, wikidata or hybrid")
    return mode


def _build_seed_input(country_iso3_codes: set[str], mode: str) -> tuple[list[GovernmentSeed], dict[str, int | str]]:
    if mode == "pilot":
        return list(PILOT_GOVERNMENTS), {
            "seed_source": "pilot",
            "wikidata_rows": 0,
            "pilot_rows": len(PILOT_GOVERNMENTS),
        }

    client = WikidataGovernmentsClient(
        timeout_seconds=settings.etl_governments_timeout_seconds,
        chunk_size=settings.etl_governments_chunk_size,
        max_duration_seconds=settings.etl_governments_max_duration_seconds,
    )
    try:
        periods = client.fetch_periods(
            country_iso3_codes,
            min_start_year=settings.etl_governments_min_start_year,
        )
    except Exception as exc:
        if mode == "hybrid":
            logger.warning(
                "Governments seed fallback to pilot due to wikidata error: %s",
                exc,
            )
            return list(PILOT_GOVERNMENTS), {
                "seed_source": "hybrid_fallback_pilot",
                "wikidata_rows": 0,
                "pilot_rows": len(PILOT_GOVERNMENTS),
            }
        raise

    wikidata_seeds = [
        GovernmentSeed(
            iso3=period.iso3,
            leader_name=period.leader_name,
            party=None,
            start_date=period.start_date,
            end_date=period.end_date,
            political_lean=None,
        )
        for period in periods
    ]

    if mode == "wikidata":
        return wikidata_seeds, {
            "seed_source": "wikidata",
            "wikidata_rows": len(wikidata_seeds),
            "pilot_rows": 0,
        }

    merged = _merge_wikidata_with_pilot(wikidata_seeds)
    return merged, {
        "seed_source": "hybrid",
        "wikidata_rows": len(wikidata_seeds),
        "pilot_rows": len(PILOT_GOVERNMENTS),
    }


def _seed_governments_with_session(db: Session, mode: str) -> dict[str, int | str]:
    country_rows = db.execute(select(Country.id, Country.iso3)).all()
    country_map = {iso3: country_id for country_id, iso3 in country_rows}

    seed_input, metadata = _build_seed_input(set(country_map.keys()), mode)

    payload = []
    missing_countries: set[str] = set()

    for gov in seed_input:
        country_id = country_map.get(gov.iso3)
        if not country_id:
            missing_countries.add(gov.iso3)
            continue

        payload.append(
            {
                "country_id": country_id,
                "leader_name": gov.leader_name,
                "party": gov.party,
                "start_date": gov.start_date,
                "end_date": gov.end_date,
                "political_lean": gov.political_lean,
            }
        )

    if payload:
        stmt = insert(Government).values(payload)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_government_country_leader_start",
            set_={
                "party": stmt.excluded.party,
                "end_date": stmt.excluded.end_date,
                "political_lean": stmt.excluded.political_lean,
            },
        )
        db.execute(stmt)

    return {
        **metadata,
        "rows_prepared": len(payload),
        "rows_seed_input": len(seed_input),
        "missing_countries": len(missing_countries),
        "countries_requested": len(country_map),
    }


def seed_governments(source: str | None = None, db: Session | None = None) -> dict[str, int | str]:
    mode = _resolve_seed_mode(source)
    logger.info("Starting governments seed with mode=%s", mode)

    if db is None:
        with SessionLocal.begin() as managed_db:
            result = _seed_governments_with_session(managed_db, mode)
    else:
        result = _seed_governments_with_session(db, mode)

    logger.info("Governments seed completed: %s", result)
    return result


def main() -> None:
    result = seed_governments()
    print("Government seed completed:", result)


if __name__ == "__main__":
    main()
