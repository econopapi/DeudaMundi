from pathlib import Path
import re

from pydantic_settings import BaseSettings, SettingsConfigDict


LOCAL_NETWORK_CORS_REGEX = (
    r"^https?://(localhost|127\\.0\\.0\\.1|0\\.0\\.0\\.0"
    r"|10\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}"
    r"|172\\.(1[6-9]|2\\d|3[0-1])\\.\\d{1,3}\\.\\d{1,3}"
    r"|192\\.168\\.\\d{1,3}\\.\\d{1,3}"
    r"|[a-zA-Z0-9-]+\\.local)(:\\d+)?$"
)


def normalize_sqlalchemy_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def normalize_development_database_host(
    url: str,
    app_env: str,
    running_in_docker: bool | None = None,
) -> str:
    if app_env.lower() != "development":
        return url

    if running_in_docker is None:
        running_in_docker = Path("/.dockerenv").exists()

    if running_in_docker:
        return url

    # When running API directly on host, docker DNS name `postgres` is not resolvable.
    return re.sub(r"@postgres(?=[:/])", "@localhost", url, count=1)


class Settings(BaseSettings):
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/deudamundi"
    supabase_database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    cors_allowed_origins: str = "http://localhost:5173"
    cors_allow_origin_regex: str | None = None
    rate_limit_requests_per_minute: int = 100
    security_hsts_enabled: bool = False
    admin_api_key: str | None = None

    etl_scheduler_enabled: bool = False
    etl_schedule_cron: str = "0 2 1 2 *"
    etl_allow_proxy_debt_fallback: bool = False
    etl_seed_governments_enabled: bool = True
    etl_governments_source: str = "hybrid"
    etl_governments_min_start_year: int = 1990
    etl_governments_timeout_seconds: float = 30.0
    etl_governments_chunk_size: int = 25
    etl_governments_max_duration_seconds: float = 180.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def effective_database_url(self) -> str:
        raw_url = self.supabase_database_url or self.database_url
        normalized = normalize_sqlalchemy_database_url(raw_url)
        return normalize_development_database_host(normalized, self.app_env)

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def cors_allow_origin_regex_effective(self) -> str | None:
        if self.cors_allow_origin_regex:
            return self.cors_allow_origin_regex

        if self.app_env.lower() != "production":
            return LOCAL_NETWORK_CORS_REGEX

        return None


settings = Settings()
