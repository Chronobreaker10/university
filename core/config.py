import logging
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT
    date_format: str = "%Y-%m-%d %H:%M:%S"

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class DatabaseConfig(BaseModel):
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    host: str = "localhost"
    user: str = "postgres"
    password: str = "postgres"
    port: int = 5433
    name: str = "university"

    @property
    def url(self) -> str:
        return str(PostgresDsn(f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"))


class SecurityConfig(BaseModel):
    cookie_name: str = "access_token"
    secret_key: str
    algorithm: str
    expires_minutes: int = 30


class Settings(BaseSettings):
    db: DatabaseConfig
    security: SecurityConfig
    run: RunConfig = RunConfig()
    logging: LoggingConfig = LoggingConfig()
    TEST_DATABASE_URL: str = "sqlite+aiosqlite://"
    model_config = SettingsConfigDict(env_file=(".env.template", ".env"), case_sensitive=False,
                                      env_nested_delimiter="__")


settings = Settings()
