import os
from functools import lru_cache

from app.core.settings.base import BaseAppSettings
from app.core.settings.environments import (
    DevelopmentSettings,
    ProductionSettings,
    TestingSettings,
)

SETTINGS_MAP: dict[str, type[BaseAppSettings]] = {
    "development": DevelopmentSettings,
    "testing": TestingSettings,
    "production": ProductionSettings,
}


@lru_cache
def get_settings() -> BaseAppSettings:
    environment = os.getenv("APP_ENV", "development").lower()
    settings_class = SETTINGS_MAP.get(environment, DevelopmentSettings)
    return settings_class()


settings = get_settings()

__all__ = ["BaseAppSettings", "get_settings", "settings"]

