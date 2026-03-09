from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "WB Wrapper"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    cors_origins: str = "http://localhost:3000"

    wb_timeout_seconds: int = 30
    wb_retries: int = 0
    wb_client_secret: str = Field(default="", alias="WB_CLIENT_SECRET")
    wb_user_agent: str
    wb_authorization_template: str = "{token}"
    admin_username: str = "admin"
    admin_authorization_token: str = Field(default="admin-local-token", alias="ADMIN_AUTHORIZATION_TOKEN")

    auth_base_url: str = "http://token-validator-mock:9000"
    auth_issue_path: str = "/auth/issue"
    auth_verify_path: str = "/auth/verify"
    auth_timeout_seconds: int = 10

    database_url_async: str = "sqlite+aiosqlite:///./app.db"
    database_url_sync: str = "sqlite:///./app.db"

    clickhouse_url: str = "http://clickhouse:8123"
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "default"

    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
