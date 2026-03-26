from functools import lru_cache

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        cache_strings=False,
        extra="ignore",
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
    testing: bool = False
    debug_username: str = "debug"
    admin_username: str = "admin"

    cors_origins: str = "http://localhost:3000"

    wb_timeout_seconds: int = 30
    wb_retries: int = 0
    wb_client_secret: str = ""
    wb_user_agent: str

    debug_authorization_token: str = "debug-local-token"

    auth_base_url: str = "http://host.docker.internal:5005"
    auth_send_code: str = "/api/authentication/support/send-otp"
    auth_verify_code: str = "/api/authentication/support/check-otp"
    auth_verify_token: str = "/api/authentication/support/verify-token"
    auth_timeout_seconds: int = 10

    test_database_url_async: str = "sqlite+aiosqlite:///./app.db"
    test_database_url_sync: str = "sqlite:///./app.db"

    db_user: str
    db_pass: str
    db_host: str
    db_port: int
    db_name: str

    adv_db_user: str
    adv_db_pass: str
    adv_db_host: str
    adv_db_port: int
    adv_db_name: str

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

    @property
    def adv_database_url_asyncpg(self):
        return f"postgresql+asyncpg://{self.adv_db_user}:{self.adv_db_pass}@{self.adv_db_host}:{self.adv_db_port}/{self.adv_db_name}"

    @property
    def adv_database_url_syncpg(self):
        return f"postgresql://{self.adv_db_user}:{self.adv_db_pass}@{self.adv_db_host}:{self.adv_db_port}/{self.adv_db_name}"

    @property
    def verify_token_url(self) -> str:
        return f"{self.auth_base_url.rstrip('/')}/{self.auth_verify_token.lstrip('/')}"

    @property
    def send_code_url(self) -> str:
        return f"{self.auth_base_url.rstrip('/')}/{self.auth_send_code.lstrip('/')}"

    @property
    def verify_code_url(self) -> str:
        return f"{self.auth_base_url.rstrip('/')}/{self.auth_verify_code.lstrip('/')}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
