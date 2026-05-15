from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, session: AsyncSession, *, email: str) -> User | None:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: UserCreate,
    ) -> User:
        user_data = obj_in.model_dump(exclude={"password"})
        db_obj = User(
            **user_data,
            password_hash=hash_password(obj_in.password),
        )
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate,
    ) -> User:
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        )
        if "password" in update_data:
            update_data["password_hash"] = hash_password(update_data.pop("password"))
        return await super().update(session, db_obj=db_obj, obj_in=update_data)


user_crud = CRUDUser(User)
