from app.core.settings.base import BaseAppSettings


class DevelopmentSettings(BaseAppSettings):
    app_env: str = "development"
    log_level: str = "DEBUG"


class TestingSettings(BaseAppSettings):
    app_env: str = "testing"
    database_url: str = "sqlite+aiosqlite:///./test.db"
    auto_create_tables: bool = False
    log_level: str = "DEBUG"


class ProductionSettings(BaseAppSettings):
    app_env: str = "production"
    auto_create_tables: bool = False
    log_level: str = "INFO"

