import logging
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn, AmqpDsn

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)


class RunConfig(BaseModel):
    host: str = "localhost"
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
    access_token_cookie_name: str = "access_token"
    refresh_token_cookie_name: str = "refresh_token"
    secret_key: str
    algorithm: str
    access_token_expires_minutes: int = 15
    refresh_token_expires_days: int = 30
    refresh_token_key: str = "refresh_tokens"


class CsrfConfig(BaseModel):
    secret_key: str
    cookie_samesite: str = "none"
    cookie_secure: bool = True
    token_location: Literal["header", "body"] = "body"
    token_key: str = "csrf_secret_token"


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int = 1
    prefix: str = "university"


class CacheConfig(BaseModel):
    prefix: str = "fastapi-cache"
    db_name: int = 0


class FastStreamConfig(BaseModel):
    rabbitmq_url: AmqpDsn


class MailConfig(BaseModel):
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_email: str = "admin@university.ru"
    smtp_password: str = ""
    templates_path: Path = Path(__file__).parent.parent / "templates" / "email"


class Settings(BaseSettings):
    db: DatabaseConfig
    security: SecurityConfig
    csrf: CsrfConfig
    cache: CacheConfig = CacheConfig()
    redis: RedisConfig
    run: RunConfig = RunConfig()
    logging: LoggingConfig = LoggingConfig()
    fast_stream: FastStreamConfig
    mail: MailConfig = MailConfig()
    TEST_DATABASE_URL: str = "sqlite+aiosqlite://"
    ENV: Literal["dev", "prod"] = "prod"
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__"
    )


settings = Settings()
