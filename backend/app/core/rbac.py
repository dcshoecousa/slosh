from pathlib import Path

import casbin
from casbin_async_sqlalchemy_adapter import Adapter
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationException
from app.models.enums import UserRole
from app.models.casbin_rule import CasbinRule
from app.models.user import User


MODEL_PATH = Path(__file__).resolve().parent.parent / "rbac" / "model.conf"
USER_SUBJECT_PREFIX = "user:"
VALID_ROLE_VALUES = {role.value for role in UserRole}


async def _build_enforcer(session: AsyncSession | None = None) -> casbin.AsyncEnforcer:
    from app.db.database import engine

    adapter = Adapter(
        engine,
        db_class=CasbinRule,
        db_session=session,
    )
    enforcer = casbin.AsyncEnforcer(str(MODEL_PATH), adapter)
    await enforcer.load_policy()
    return enforcer


def _split_policy_rules() -> tuple[list[list[str]], list[list[str]]]:
    from app.rbac.default_policy import DEFAULT_POLICY_RULES

    permission_rules: list[list[str]] = []
    grouping_rules: list[list[str]] = []

    for ptype, *values in DEFAULT_POLICY_RULES:
        rule = [value for value in values if value]
        if ptype == "p":
            permission_rules.append(rule)
        elif ptype == "g":
            grouping_rules.append(rule)

    return permission_rules, grouping_rules


async def seed_default_policies(session: AsyncSession) -> None:
    result = await session.execute(select(func.count()).select_from(CasbinRule))
    if int(result.scalar_one()) > 0:
        return

    enforcer = await _build_enforcer(session)
    permission_rules, grouping_rules = _split_policy_rules()

    if permission_rules:
        await enforcer.add_policies(permission_rules)
    if grouping_rules:
        await enforcer.add_grouping_policies(grouping_rules)

    await session.flush()


def build_user_subject(user_id: int) -> str:
    return f"{USER_SUBJECT_PREFIX}{user_id}"


def _parse_user_subject(subject: str) -> int | None:
    if not subject.startswith(USER_SUBJECT_PREFIX):
        return None

    raw_user_id = subject.removeprefix(USER_SUBJECT_PREFIX)
    if not raw_user_id.isdigit():
        return None

    return int(raw_user_id)


async def get_user_roles_map(
    session: AsyncSession,
    user_ids: list[int],
) -> dict[int, UserRole]:
    if not user_ids:
        return {}

    subjects = [build_user_subject(user_id) for user_id in user_ids]
    result = await session.execute(
        select(CasbinRule.v0, CasbinRule.v1).where(
            CasbinRule.ptype == "g",
            CasbinRule.v0.in_(subjects),
        )
    )

    role_map: dict[int, UserRole] = {}
    for subject, role in result.all():
        if not subject or not role or role not in VALID_ROLE_VALUES:
            continue

        user_id = _parse_user_subject(subject)
        if user_id is None:
            continue

        role_map[user_id] = UserRole(role)

    return {
        user_id: role_map.get(user_id, UserRole.MEMBER)
        for user_id in user_ids
    }


async def get_user_roles_map_list(
    session: AsyncSession,
    user_ids: list[int],
) -> dict[int, list[UserRole]]:
    if not user_ids:
        return {}

    subjects = [build_user_subject(user_id) for user_id in user_ids]
    result = await session.execute(
        select(CasbinRule.v0, CasbinRule.v1).where(
            CasbinRule.ptype == "g",
            CasbinRule.v0.in_(subjects),
        )
    )

    role_map: dict[int, list[UserRole]] = {user_id: [] for user_id in user_ids}
    for subject, role in result.all():
        if not subject or not role or role not in VALID_ROLE_VALUES:
            continue

        user_id = _parse_user_subject(subject)
        if user_id is None or user_id not in role_map:
            continue

        parsed_role = UserRole(role)
        if parsed_role not in role_map[user_id]:
            role_map[user_id].append(parsed_role)

    for user_id, roles in role_map.items():
        if not roles:
            roles.append(UserRole.MEMBER)
        roles.sort(key=lambda item: item.value)

    return role_map


async def get_user_role(
    session: AsyncSession,
    user_or_id: User | int,
) -> UserRole:
    user_id = user_or_id.id if isinstance(user_or_id, User) else user_or_id
    return (await get_user_roles_map(session, [user_id]))[user_id]


async def get_user_roles(
    session: AsyncSession,
    user_or_id: User | int,
) -> list[UserRole]:
    user_id = user_or_id.id if isinstance(user_or_id, User) else user_or_id
    return (await get_user_roles_map_list(session, [user_id]))[user_id]


async def set_role_for_user(
    session: AsyncSession,
    user_or_id: User | int,
    role: UserRole,
) -> None:
    user_id = user_or_id.id if isinstance(user_or_id, User) else user_or_id
    enforcer = await _build_enforcer(session)
    subject = build_user_subject(user_id)

    await enforcer.delete_roles_for_user(subject)
    await enforcer.add_role_for_user(subject, role.value)
    await session.flush()


async def clear_roles_for_user(
    session: AsyncSession,
    user_or_id: User | int,
) -> None:
    user_id = user_or_id.id if isinstance(user_or_id, User) else user_or_id
    enforcer = await _build_enforcer(session)
    await enforcer.delete_roles_for_user(build_user_subject(user_id))
    await session.flush()


async def count_users_with_role(
    session: AsyncSession,
    role: UserRole,
) -> int:
    result = await session.execute(
        select(CasbinRule.v0).where(
            CasbinRule.ptype == "g",
            CasbinRule.v1 == role.value,
        )
    )
    subjects = {
        subject
        for (subject,) in result.all()
        if subject and _parse_user_subject(subject) is not None
    }
    return len(subjects)


async def enforce_permission(
    session: AsyncSession,
    user: User,
    resource: str,
    action: str,
) -> None:
    allowed = await has_permission_for_user(session, user, resource, action)
    if not allowed:
        raise AuthorizationException(
            f"User '{user.id}' is not allowed to {action} on {resource}."
        )


async def list_permissions_for_role(
    session: AsyncSession,
    role: str,
) -> list[tuple[str, str]]:
    enforcer = await _build_enforcer(session)
    result = await enforcer.get_implicit_permissions_for_user(role)
    permissions = {
        (rule[1], rule[2])
        for rule in result
        if len(rule) >= 3 and rule[1] and rule[2]
    }
    return sorted(permissions, key=lambda item: (item[0], item[1]))


async def list_permissions_for_user(
    session: AsyncSession,
    user_or_id: User | int,
) -> list[tuple[str, str]]:
    user_id = user_or_id.id if isinstance(user_or_id, User) else user_or_id
    enforcer = await _build_enforcer(session)
    result = await enforcer.get_implicit_permissions_for_user(build_user_subject(user_id))
    permissions = {
        (rule[1], rule[2])
        for rule in result
        if len(rule) >= 3 and rule[1] and rule[2]
    }
    return sorted(permissions, key=lambda item: (item[0], item[1]))


async def has_permission(
    session: AsyncSession,
    role: str,
    resource: str,
    action: str,
) -> bool:
    enforcer = await _build_enforcer(session)
    return bool(enforcer.enforce(role, resource, action))


async def has_permission_for_user(
    session: AsyncSession,
    user_or_id: User | int,
    resource: str,
    action: str,
) -> bool:
    user_id = user_or_id.id if isinstance(user_or_id, User) else user_or_id
    return await has_permission(session, build_user_subject(user_id), resource, action)


async def add_permission_for_role(
    session: AsyncSession,
    role: str,
    resource: str,
    action: str,
) -> bool:
    enforcer = await _build_enforcer(session)
    added = await enforcer.add_permission_for_user(role, resource, action)
    if added:
        await session.flush()

    return added


async def remove_permission_for_role(
    session: AsyncSession,
    role: str,
    resource: str,
    action: str,
) -> bool:
    enforcer = await _build_enforcer(session)
    removed = await enforcer.delete_permission_for_user(role, resource, action)
    if removed:
        await session.flush()

    return removed
