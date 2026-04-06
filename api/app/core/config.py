from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_sqlalchemy_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/deudamundi"
    supabase_database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    cors_allowed_origins: str = "http://localhost:5173"
    rate_limit_requests_per_minute: int = 100
    security_hsts_enabled: bool = False
    admin_api_key: str | None = None

    etl_scheduler_enabled: bool = False
    etl_schedule_cron: str = "0 2 1 2 *"
    etl_allow_proxy_debt_fallback: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def effective_database_url(self) -> str:
        raw_url = self.supabase_database_url or self.database_url
        return normalize_sqlalchemy_database_url(raw_url)

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


settings = Settings()
