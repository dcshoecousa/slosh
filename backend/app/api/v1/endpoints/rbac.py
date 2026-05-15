from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_permission
from app.api.responses import build_success_response
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.rbac import (
    CurrentUserPermissionsRead,
    PermissionCheckRead,
    RolePermissionMutation,
    RolePermissionsRead,
    UserRoleMutation,
)
from app.services.rbac_service import (
    assign_role_to_user,
    check_user_permission,
    get_current_user_permissions,
    get_role_permissions,
    grant_permission_to_role,
    remove_role_from_user,
    revoke_permission_from_role,
)

router = APIRouter(prefix="/rbac")


@router.get(
    "/me/permissions",
    response_model=ApiResponse[CurrentUserPermissionsRead],
)
async def read_current_user_permissions(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_permission("rbac", "read")),
) -> ApiResponse[CurrentUserPermissionsRead]:
    return build_success_response(
        request,
        data=await get_current_user_permissions(session, current_user),
        message="Current user permissions fetched successfully.",
    )


@router.get(
    "/roles/{role}/permissions",
    response_model=ApiResponse[RolePermissionsRead],
)
async def read_role_permissions(
    request: Request,
    role: UserRole,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("rbac", "inspect")),
) -> ApiResponse[RolePermissionsRead]:
    return build_success_response(
        request,
        data=await get_role_permissions(session, role),
        message="Role permissions fetched successfully.",
    )


@router.post(
    "/users/{user_id}/roles",
    response_model=ApiResponse[CurrentUserPermissionsRead],
)
async def add_role_to_user(
    request: Request,
    user_id: int,
    payload: UserRoleMutation,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("rbac", "assign_role")),
) -> ApiResponse[CurrentUserPermissionsRead]:
    user = await assign_role_to_user(session, user_id=user_id, payload=payload)
    return build_success_response(
        request,
        data=await get_current_user_permissions(session, user),
        message="User role assigned successfully.",
    )


@router.delete(
    "/users/{user_id}/roles/{role}",
    response_model=ApiResponse[CurrentUserPermissionsRead],
)
async def remove_user_role(
    request: Request,
    user_id: int,
    role: UserRole,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("rbac", "revoke_role")),
) -> ApiResponse[CurrentUserPermissionsRead]:
    user = await remove_role_from_user(session, user_id=user_id, role=role)
    return build_success_response(
        request,
        data=await get_current_user_permissions(session, user),
        message="User role removed successfully.",
    )


@router.get(
    "/check",
    response_model=ApiResponse[PermissionCheckRead],
)
async def check_current_user_permission(
    request: Request,
    resource: str = Query(min_length=1),
    action: str = Query(min_length=1),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_permission("rbac", "check")),
) -> ApiResponse[PermissionCheckRead]:
    return build_success_response(
        request,
        data=await check_user_permission(session, current_user, resource, action),
        message="Permission check completed successfully.",
    )


@router.post(
    "/roles/{role}/permissions",
    response_model=ApiResponse[RolePermissionsRead],
)
async def add_permission_to_role(
    request: Request,
    role: UserRole,
    payload: RolePermissionMutation,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("rbac", "grant_permission")),
) -> ApiResponse[RolePermissionsRead]:
    return build_success_response(
        request,
        data=await grant_permission_to_role(session, role, payload),
        message="Role permission added successfully.",
    )


@router.delete(
    "/roles/{role}/permissions",
    response_model=ApiResponse[RolePermissionsRead],
)
async def remove_permission_from_role(
    request: Request,
    role: UserRole,
    payload: RolePermissionMutation,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_permission("rbac", "revoke_permission")),
) -> ApiResponse[RolePermissionsRead]:
    return build_success_response(
        request,
        data=await revoke_permission_from_role(session, role, payload),
        message="Role permission removed successfully.",
    )
