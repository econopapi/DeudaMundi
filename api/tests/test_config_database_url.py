from app.core.config import Settings, normalize_development_database_host


def test_effective_database_url_normalizes_postgresql_scheme() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql://local_user:local_pass@localhost:5432/local_db",
        supabase_database_url="postgresql://user:pass@db.supabase.co:5432/postgres?sslmode=require",
    )

    assert settings.effective_database_url.startswith("postgresql+psycopg://")


def test_effective_database_url_keeps_explicit_driver() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://local_user:local_pass@localhost:5432/local_db",
        supabase_database_url=None,
    )

    assert settings.effective_database_url == settings.database_url


def test_etl_proxy_fallback_default_is_disabled() -> None:
    settings = Settings(_env_file=None)

    assert settings.etl_allow_proxy_debt_fallback is False


def test_etl_proxy_fallback_can_be_enabled_explicitly() -> None:
    settings = Settings(_env_file=None, etl_allow_proxy_debt_fallback=True)

    assert settings.etl_allow_proxy_debt_fallback is True


def test_cors_local_network_regex_enabled_in_development() -> None:
    settings = Settings(_env_file=None, app_env="development")

    assert settings.cors_allow_origin_regex_effective is not None


def test_cors_local_network_regex_disabled_by_default_in_production() -> None:
    settings = Settings(_env_file=None, app_env="production")

    assert settings.cors_allow_origin_regex_effective is None


def test_development_database_host_falls_back_to_localhost_outside_docker() -> None:
    url = "postgresql+psycopg://postgres:postgres@postgres:5432/deudamundi"

    normalized = normalize_development_database_host(url, "development", running_in_docker=False)

    assert normalized == "postgresql+psycopg://postgres:postgres@localhost:5432/deudamundi"


def test_development_database_host_keeps_postgres_inside_docker() -> None:
    url = "postgresql+psycopg://postgres:postgres@postgres:5432/deudamundi"

    normalized = normalize_development_database_host(url, "development", running_in_docker=True)

    assert normalized == url
