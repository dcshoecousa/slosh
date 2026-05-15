from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.rbac import (
    add_permission_for_role,
    count_users_with_role,
    get_user_role,
    get_user_roles,
    has_permission_for_user,
    list_permissions_for_role,
    list_permissions_for_user,
    remove_permission_for_role,
    set_role_for_user,
)
from app.crud.user import user_crud
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.rbac import (
    CurrentUserPermissionsRead,
    PermissionCheckRead,
    PermissionRead,
    RolePermissionMutation,
    RolePermissionsRead,
    UserRoleMutation,
)


async def _build_permission_reads(
    session: AsyncSession,
    role: UserRole | str,
) -> list[PermissionRead]:
    return [
        PermissionRead(resource=resource, action=action)
        for resource, action in await list_permissions_for_role(session, str(role))
    ]


async def get_current_user_permissions(
    session: AsyncSession,
    user: User,
) -> CurrentUserPermissionsRead:
    return CurrentUserPermissionsRead(
        user_id=user.id,
        roles=await get_user_roles(session, user.id),
        permissions=[
            PermissionRead(resource=resource, action=action)
            for resource, action in await list_permissions_for_user(session, user.id)
        ],
    )


async def get_role_permissions(
    session: AsyncSession,
    role: UserRole,
) -> RolePermissionsRead:
    return RolePermissionsRead(
        role=role,
        permissions=await _build_permission_reads(session, role),
    )


async def check_user_permission(
    session: AsyncSession,
    user: User,
    resource: str,
    action: str,
) -> PermissionCheckRead:
    return PermissionCheckRead(
        user_id=user.id,
        roles=await get_user_roles(session, user.id),
        resource=resource,
        action=action,
        allowed=await has_permission_for_user(session, user.id, resource, action),
    )


async def assign_role_to_user(
    session: AsyncSession,
    *,
    user_id: int,
    payload: UserRoleMutation,
) -> User:
    user = await _get_user_by_id(session, user_id)
    current_role = await get_user_role(session, user.id)

    if current_role == payload.role:
        raise ConflictException("User already has this role.")

    await set_role_for_user(session, user.id, payload.role)
    return user


async def remove_role_from_user(
    session: AsyncSession,
    *,
    user_id: int,
    role: UserRole,
) -> User:
    user = await _get_user_by_id(session, user_id)
    current_role = await get_user_role(session, user.id)

    if current_role != role:
        raise ConflictException("User does not have this role.")
    if role == UserRole.MEMBER:
        raise ConflictException("Cannot remove the default member role.")

    admin_count = await count_users_with_role(session, role=UserRole.ADMIN)
    if role == UserRole.ADMIN and admin_count <= 1:
        raise ConflictException("Cannot remove the last admin role.")

    await set_role_for_user(session, user.id, UserRole.MEMBER)
    return user


async def grant_permission_to_role(
    session: AsyncSession,
    role: UserRole,
    payload: RolePermissionMutation,
) -> RolePermissionsRead:
    added = await add_permission_for_role(
        session,
        role.value,
        payload.resource,
        payload.action,
    )
    if not added:
        raise ConflictException("This permission already exists for the role.")
    return await get_role_permissions(session, role)


async def revoke_permission_from_role(
    session: AsyncSession,
    role: UserRole,
    payload: RolePermissionMutation,
) -> RolePermissionsRead:
    removed = await remove_permission_for_role(
        session,
        role.value,
        payload.resource,
        payload.action,
    )
    if not removed:
        raise NotFoundException("This permission does not exist for the role.")
    return await get_role_permissions(session, role)


async def _get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user = await user_crud.get(session, user_id)
    if user is None:
        raise NotFoundException("User not found.")
    return user
