from collections.abc import AsyncGenerator
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException, ConflictException, DatabaseException
from app.core.rbac import enforce_permission
from app.core.security import decode_access_token
from app.crud.user import user_crud
from app.db.database import AsyncSessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            if session.in_transaction():
                await session.commit()
        except IntegrityError as exc:
            if session.in_transaction():
                await session.rollback()
            raise ConflictException("Database constraint violation.") from exc
        except SQLAlchemyError as exc:
            if session.in_transaction():
                await session.rollback()
            raise DatabaseException() from exc
        except Exception:
            if session.in_transaction():
                await session.rollback()
            raise


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_db_session),
) -> User:
    payload = decode_access_token(token)
    subject = payload.get("sub")

    if subject is None or not str(subject).isdigit():
        raise AuthenticationException("Invalid token subject.")

    user = await user_crud.get(session, int(subject))
    if user is None:
        raise AuthenticationException("User not found.")
    if not user.is_active:
        raise AuthenticationException("Inactive user.")
    return user


def require_permission(resource: str, action: str) -> Callable:
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ) -> User:
        await enforce_permission(session, current_user, resource, action)
        return current_user

    return permission_dependency
