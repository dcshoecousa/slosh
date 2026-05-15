from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import clear_roles_for_user, get_user_role, get_user_roles_map, set_role_for_user
from app.core.exceptions import ConflictException, NotFoundException
from app.crud.user import user_crud
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate


async def create_user(session: AsyncSession, payload: UserCreate) -> User:
    return await create_user_with_role(session, payload, role=None)


async def create_user_with_role(
    session: AsyncSession,
    payload: UserCreate,
    *,
    role: UserRole | None,
) -> User:
    existing_user = await user_crud.get_by_email(session, email=payload.email)
    if existing_user is not None:
        raise ConflictException("User with this email already exists.")

    user = await user_crud.create(session, obj_in=payload)
    await set_role_for_user(session, user.id, role or UserRole.MEMBER)
    return user


async def list_users(
    session: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[User], int]:
    users = await user_crud.get_multi(session, skip=skip, limit=limit)
    total = await user_crud.count(session)
    return users, total


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user = await user_crud.get(session, user_id)
    if user is None:
        raise NotFoundException("User not found.")
    return user


async def build_user_read(session: AsyncSession, user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        role=await get_user_role(session, user.id),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


async def build_user_reads(
    session: AsyncSession,
    users: list[User],
) -> list[UserRead]:
    role_map = await get_user_roles_map(session, [user.id for user in users])
    return [
        UserRead(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            role=role_map[user.id],
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user in users
    ]


async def update_user(
    session: AsyncSession,
    *,
    user_id: int,
    payload: UserUpdate,
) -> User:
    user = await get_user_by_id(session, user_id)

    if payload.email and payload.email != user.email:
        existing_user = await user_crud.get_by_email(session, email=payload.email)
        if existing_user is not None:
            raise ConflictException("User with this email already exists.")

    return await user_crud.update(session, db_obj=user, obj_in=payload)


async def delete_user(session: AsyncSession, *, user_id: int) -> None:
    user = await get_user_by_id(session, user_id)
    await clear_roles_for_user(session, user.id)
    await user_crud.delete(session, item_id=user_id)
