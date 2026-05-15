from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_permission
from app.api.responses import build_success_response
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import (
    build_user_read,
    build_user_reads,
    create_user,
    delete_user,
    get_user_by_id,
    list_users,
    update_user,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ApiResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_user_endpoint(
    request: Request,
    payload: UserCreate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("users", "create")),
) -> ApiResponse[UserRead]:
    user = await create_user(session, payload)
    return build_success_response(
        request,
        data=await build_user_read(session, user),
        message="User created successfully.",
    )


@router.get("/", response_model=ApiResponse[PaginatedResponse[UserRead]])
async def list_users_endpoint(
    request: Request,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("users", "read")),
) -> ApiResponse[PaginatedResponse[UserRead]]:
    users, total = await list_users(session, skip=skip, limit=limit)
    return build_success_response(
        request,
        data=PaginatedResponse[UserRead](
            items=await build_user_reads(session, users),
            total=total,
            skip=skip,
            limit=limit,
        ),
        message="Users fetched successfully.",
    )


@router.get("/{user_id}", response_model=ApiResponse[UserRead])
async def get_user_endpoint(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("users", "read")),
) -> ApiResponse[UserRead]:
    user = await get_user_by_id(session, user_id)
    return build_success_response(
        request,
        data=await build_user_read(session, user),
        message="User fetched successfully.",
    )


@router.patch("/{user_id}", response_model=ApiResponse[UserRead])
async def update_user_endpoint(
    request: Request,
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("users", "update")),
) -> ApiResponse[UserRead]:
    user = await update_user(session, user_id=user_id, payload=payload)
    return build_success_response(
        request,
        data=await build_user_read(session, user),
        message="User updated successfully.",
    )


@router.delete("/{user_id}", response_model=ApiResponse[None])
async def delete_user_endpoint(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("users", "delete")),
) -> ApiResponse[None]:
    await delete_user(session, user_id=user_id)
    return build_success_response(
        request,
        message="User deleted successfully.",
    )
