from typing import Literal

from pydantic import BaseModel


class UserSettingsRead(BaseModel):
    theme: Literal["light", "dark"] = "light"
    sidebar_collapsed: bool = False


class UserSettingsUpdate(BaseModel):
    theme: Literal["light", "dark"] | None = None
    sidebar_collapsed: bool | None = None
