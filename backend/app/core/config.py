from functools import lru_cache

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        cache_strings=False,
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        )
    )

    app_name: str = "WB Wrapper"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    debug_username: str = "debug"

    cors_origins: str = "http://localhost:3000"

    wb_timeout_seconds: int = 30
    wb_retries: int = 0
    wb_client_secret: str = Field(default="", alias="WB_CLIENT_SECRET")
    wb_user_agent: str
    wb_authorization_template: str = "{token}"
    admin_username: str = "admin"
    admin_authorization_token: str = Field(default="admin-local-token", alias="ADMIN_AUTHORIZATION_TOKEN")
    debug_authorization_token: str = Field(default="debug-local-token", alias="DEBUG_AUTHORIZATION_TOKEN")

    auth_base_url: str = "http://token-validator-mock:9000"
    auth_issue_path: str = "/auth/issue"
    auth_verify_path: str = "/auth/verify"
    auth_timeout_seconds: int = 10

    test_database_url_async: str = "sqlite+aiosqlite:///./app.db"
    test_database_url_sync: str = "sqlite:///./app.db"

    db_user: str
    db_pass: str
    db_host: str
    db_port: int
    db_name: str

    clickhouse_url: str = "http://clickhouse:8123"
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "default"

    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url_asyncpg(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def database_url_syncpg(self):
        return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
