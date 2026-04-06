from datetime import UTC, date, datetime

from app.db.base_class import Base
from app.db.session import get_db
from app.main import app
from app.models import Country, DebtRecord, Government
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


def _build_test_client() -> tuple[TestClient, sessionmaker[Session]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        class_=Session,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():  # type: ignore[no-untyped-def]
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), TestingSessionLocal


def _seed_sample_data(session_local: sessionmaker[Session]) -> None:
    with session_local.begin() as db:
        arg = Country(
            iso2="AR",
            iso3="ARG",
            name_es="Argentina",
            name_en="Argentina",
            region="Latin America & Caribbean",
            subregion="South America",
            population=46000000,
            capital="Buenos Aires",
            flag_url=None,
        )
        usa = Country(
            iso2="US",
            iso3="USA",
            name_es="Estados Unidos",
            name_en="United States",
            region="North America",
            subregion="North America",
            population=340000000,
            capital="Washington, D.C.",
            flag_url=None,
        )
        db.add_all([arg, usa])
        db.flush()

        db.add_all(
            [
                DebtRecord(
                    country_id=arg.id,
                    year=2023,
                    total_external_debt_usd=200.0,
                    debt_pct_gdp=50.0,
                    debt_per_capita_usd=4.0,
                    gdp_usd=400.0,
                    source="worldbank",
                    updated_at=datetime.now(UTC),
                ),
                DebtRecord(
                    country_id=arg.id,
                    year=2024,
                    total_external_debt_usd=300.0,
                    debt_pct_gdp=60.0,
                    debt_per_capita_usd=6.0,
                    gdp_usd=500.0,
                    source="worldbank",
                    updated_at=datetime.now(UTC),
                ),
                DebtRecord(
                    country_id=usa.id,
                    year=2024,
                    total_external_debt_usd=1000.0,
                    debt_pct_gdp=90.0,
                    debt_per_capita_usd=10.0,
                    gdp_usd=2000.0,
                    source="worldbank",
                    updated_at=datetime.now(UTC),
                ),
                Government(
                    country_id=arg.id,
                    leader_name="Demo Leader",
                    party="Demo Party",
                    start_date=date(2020, 1, 1),
                    end_date=None,
                    political_lean="center",
                ),
            ]
        )


def test_country_history_endpoint_reads_database() -> None:
    client, session_local = _build_test_client()
    _seed_sample_data(session_local)

    response = client.get("/api/v1/countries/ARG/history")

    assert response.status_code == 200
    payload = response.json()
    assert payload["iso3"] == "ARG"
    assert payload["items"][0]["year"] == 2024
    assert len(payload["items"]) == 2


def test_country_governments_endpoint_reads_database() -> None:
    client, session_local = _build_test_client()
    _seed_sample_data(session_local)

    response = client.get("/api/v1/countries/ARG/governments")

    assert response.status_code == 200
    payload = response.json()
    assert payload["iso3"] == "ARG"
    assert payload["items"][0]["leader_name"] == "Demo Leader"


def test_rankings_endpoint_reads_database() -> None:
    client, session_local = _build_test_client()
    _seed_sample_data(session_local)

    response = client.get("/api/v1/rankings?metric=absolute&limit=2")

    assert response.status_code == 200
    payload = response.json()
    assert payload["metric"] == "absolute"
    assert payload["items"][0]["iso3"] == "USA"
    assert payload["items"][1]["iso3"] == "ARG"
