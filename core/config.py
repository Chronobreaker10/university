import logging
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn, RedisDsn

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
    host: str = "localhost"
    user: str = "postgres"
    password: str = "postgres"
    port: int = 5433
    name: str = "university"
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    @property
    def url(self) -> str:
        return str(PostgresDsn(f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"))


class SecurityConfig(BaseModel):
    cookie_name: str = "access_token"
    secret_key: str
    algorithm: str
    expires_minutes: int = 30


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379


class CacheConfig(BaseModel):
    prefix: str = "fastapi-cache"
    db_name: int = 0


class Settings(BaseSettings):
    db: DatabaseConfig
    security: SecurityConfig
    cache: CacheConfig = CacheConfig()
    redis: RedisConfig = RedisConfig()
    run: RunConfig = RunConfig()
    logging: LoggingConfig = LoggingConfig()
    TEST_DATABASE_URL: str = "sqlite+aiosqlite://"
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__"
    )


settings = Settings()
