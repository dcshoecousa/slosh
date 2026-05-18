from app.models.user import User
from app.schemas.settings import UserSettingsRead, UserSettingsUpdate

DEFAULT_USER_SETTINGS = UserSettingsRead()


def build_user_settings(user: User) -> UserSettingsRead:
    raw_settings = user.settings or {}

    return UserSettingsRead(
        theme=raw_settings.get("theme", DEFAULT_USER_SETTINGS.theme),
        sidebar_collapsed=raw_settings.get(
            "sidebar_collapsed",
            DEFAULT_USER_SETTINGS.sidebar_collapsed,
        ),
    )


def update_user_settings(user: User, payload: UserSettingsUpdate) -> UserSettingsRead:
    current_settings = build_user_settings(user).model_dump()
    update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
    current_settings.update(update_data)
    user.settings = current_settings
    return UserSettingsRead(**current_settings)
