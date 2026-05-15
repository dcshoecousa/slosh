from pydantic import BaseModel

from app.models.enums import UserRole


class PermissionRead(BaseModel):
    resource: str
    action: str


class CurrentUserPermissionsRead(BaseModel):
    user_id: int
    roles: list[UserRole]
    permissions: list[PermissionRead]


class RolePermissionsRead(BaseModel):
    role: UserRole
    permissions: list[PermissionRead]


class PermissionCheckRead(BaseModel):
    user_id: int
    roles: list[UserRole]
    resource: str
    action: str
    allowed: bool


class UserRoleMutation(BaseModel):
    role: UserRole


class RolePermissionMutation(BaseModel):
    resource: str
    action: str
