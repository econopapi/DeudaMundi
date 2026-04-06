from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db.session import SessionLocal
from app.models import Country, Government


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


def seed_governments() -> dict[str, int]:
    with SessionLocal.begin() as db:
        country_rows = db.execute(select(Country.id, Country.iso3)).all()
        country_map = {iso3: country_id for country_id, iso3 in country_rows}

        payload = []
        missing_countries: set[str] = set()

        for gov in PILOT_GOVERNMENTS:
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
        "rows_prepared": len(payload),
        "rows_seed_input": len(PILOT_GOVERNMENTS),
        "missing_countries": len(missing_countries),
    }


def main() -> None:
    result = seed_governments()
    print("Government seed completed:", result)


if __name__ == "__main__":
    main()
