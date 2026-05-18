from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session, require_permission
from app.api.responses import build_success_response
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.common import ApiResponse
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import (
    authenticate_user,
    create_user_token,
    register_user,
)
from app.services.user_service import build_user_read

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=ApiResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
async def register_user_endpoint(
    request: Request,
    payload: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> ApiResponse[UserRead]:
    user = await register_user(session, payload)
    return build_success_response(
        request,
        data=await build_user_read(session, user),
        message="User registered successfully.",
    )


@router.post("/login", response_model=ApiResponse[Token])
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db_session),
) -> ApiResponse[Token]:
    user = await authenticate_user(session, form_data.username, form_data.password)
    return build_success_response(
        request,
        data=create_user_token(user),
        message="Login successful.",
    )


@router.post("/oauth2/token", response_model=Token, include_in_schema=False)
async def oauth2_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    return create_user_token(user)


@router.get("/me", response_model=ApiResponse[UserRead])
async def read_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_permission("auth", "read")),
) -> ApiResponse[UserRead]:
    return build_success_response(
        request,
        data=await build_user_read(session, current_user),
        message="Current user fetched successfully.",
    )
