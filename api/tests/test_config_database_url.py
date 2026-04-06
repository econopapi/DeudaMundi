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
