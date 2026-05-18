from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class BaseAppSettings(BaseSettings):
    app_name: str = "FastAPI PG Template"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        ""
    )
    auto_create_tables: bool = False
    taskiq_enabled: bool = False
    taskiq_database_url: str | None = None
    taskiq_keep_results: bool = True
    taskiq_message_table_name: str = "taskiq_messages"
    taskiq_result_table_name: str = "taskiq_results"
    taskiq_channel_name: str = "taskiq"
    taskiq_poll_interval_seconds: float = 1.0
    jwt_secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    log_level: str = "INFO"
    log_json: bool = False
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    version: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file= _PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            if not value.strip():
                return []
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def taskiq_dsn(self) -> str:
        raw_dsn = self.taskiq_database_url or self.database_url
        if raw_dsn.startswith("postgresql+"):
            scheme, rest = raw_dsn.split("://", maxsplit=1)
            return f"{scheme.split('+', maxsplit=1)[0]}://{rest}"
        return raw_dsn
