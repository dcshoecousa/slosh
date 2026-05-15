from app.core.exceptions import AuthenticationException
from app.core.security import create_access_token, verify_password
from app.crud.user import user_crud
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate
from app.services.user_service import create_user_with_role


async def register_user(session, payload: UserCreate) -> User:
    user_count = await user_crud.count(session)
    role = UserRole.ADMIN if user_count == 0 else UserRole.MEMBER
    return await create_user_with_role(session, payload, role=role)


async def authenticate_user(session, email: str, password: str) -> User:
    user = await user_crud.get_by_email(session, email=email)
    if user is None or not verify_password(password, user.password_hash):
        raise AuthenticationException("Incorrect email or password.")
    if not user.is_active:
        raise AuthenticationException("Inactive user.")
    return user


def create_user_token(user: User) -> Token:
    return Token(access_token=create_access_token(subject=str(user.id)))
