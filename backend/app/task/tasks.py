from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select

from app.core.rbac import count_users_with_role
from app.db.database import AsyncSessionLocal
from app.models.enums import UserRole
from app.models.user import User
from app.task.broker import broker


@broker.task(task_name="tasks.echo")
async def echo_message_task(
    *,
    message: str,
    requested_by: int | None = None,
) -> dict[str, Any]:
    return {
        "message": message,
        "requested_by": requested_by,
        "processed_at": datetime.now(UTC).isoformat(),
    }


@broker.task(task_name="tasks.generate_user_summary")
async def generate_user_summary_task(
    *,
    requested_by: int | None = None,
) -> dict[str, Any]:
    async with AsyncSessionLocal() as session:
        total_users_result = await session.execute(
            select(func.count()).select_from(User)
        )
        active_users_result = await session.execute(
            select(func.count()).select_from(User).where(User.is_active.is_(True))
        )

        total_users = int(total_users_result.scalar_one())
        active_users = int(active_users_result.scalar_one())
        admin_users = await count_users_with_role(session, UserRole.ADMIN)
        member_users = await count_users_with_role(session, UserRole.MEMBER)

    return {
        "requested_by": requested_by,
        "generated_at": datetime.now(UTC).isoformat(),
        "totals": {
            "users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admin_users": admin_users,
            "member_users": member_users,
        },
    }
