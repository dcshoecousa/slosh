from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.api.responses import build_success_response
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.settings import UserSettingsRead, UserSettingsUpdate
from app.services.settings_service import build_user_settings, update_user_settings

router = APIRouter(prefix="/settings")


@router.get("/me", response_model=ApiResponse[UserSettingsRead])
async def read_my_settings(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserSettingsRead]:
    return build_success_response(
        request,
        data=build_user_settings(current_user),
        message="User settings fetched successfully.",
    )


@router.patch("/me", response_model=ApiResponse[UserSettingsRead])
async def update_my_settings(
    request: Request,
    payload: UserSettingsUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserSettingsRead]:
    settings = update_user_settings(current_user, payload)
    session.add(current_user)
    await session.flush()
    await session.refresh(current_user)

    return build_success_response(
        request,
        data=settings,
        message="User settings updated successfully.",
    )
