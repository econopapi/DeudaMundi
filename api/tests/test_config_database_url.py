from app.core.config import Settings


def test_effective_database_url_normalizes_postgresql_scheme() -> None:
    settings = Settings(
        database_url="postgresql://local_user:local_pass@localhost:5432/local_db",
        supabase_database_url="postgresql://user:pass@db.supabase.co:5432/postgres?sslmode=require",
    )

    assert settings.effective_database_url.startswith("postgresql+psycopg://")


def test_effective_database_url_keeps_explicit_driver() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://local_user:local_pass@localhost:5432/local_db",
        supabase_database_url=None,
    )

    assert settings.effective_database_url == settings.database_url


def test_etl_proxy_fallback_default_is_disabled() -> None:
    settings = Settings()

    assert settings.etl_allow_proxy_debt_fallback is False


def test_etl_proxy_fallback_can_be_enabled_explicitly() -> None:
    settings = Settings(etl_allow_proxy_debt_fallback=True)

    assert settings.etl_allow_proxy_debt_fallback is True
