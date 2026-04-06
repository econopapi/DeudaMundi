from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/deudamundi"
    supabase_database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    admin_api_key: str | None = None

    etl_scheduler_enabled: bool = False
    etl_schedule_cron: str = "0 2 1 2 *"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def effective_database_url(self) -> str:
        return self.supabase_database_url or self.database_url


settings = Settings()
