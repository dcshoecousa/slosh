"""move user role links to casbin

Revision ID: 20260515_0004
Revises: 20260515_0003
Create Date: 2026-05-15 16:45:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260515_0004"
down_revision: str | None = "20260515_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    users = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("role", sa.String(length=50)),
    )
    casbin_rules = sa.table(
        "casbin_rules",
        sa.column("ptype", sa.String(length=16)),
        sa.column("v0", sa.String(length=255)),
        sa.column("v1", sa.String(length=255)),
        sa.column("v2", sa.String(length=255)),
        sa.column("v3", sa.String(length=255)),
        sa.column("v4", sa.String(length=255)),
        sa.column("v5", sa.String(length=255)),
    )

    rows = connection.execute(sa.select(users.c.id, users.c.role)).all()
    if rows:
        op.bulk_insert(
            casbin_rules,
            [
                {
                    "ptype": "g",
                    "v0": f"user:{user_id}",
                    "v1": role or "member",
                    "v2": "",
                    "v3": "",
                    "v4": "",
                    "v5": "",
                }
                for user_id, role in rows
            ],
        )

    op.drop_column("users", "role")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=50),
            nullable=False,
            server_default="member",
        ),
    )

    connection = op.get_bind()
    users = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("role", sa.String(length=50)),
    )
    casbin_rules = sa.table(
        "casbin_rules",
        sa.column("ptype", sa.String(length=16)),
        sa.column("v0", sa.String(length=255)),
        sa.column("v1", sa.String(length=255)),
    )

    rows = connection.execute(
        sa.select(casbin_rules.c.v0, casbin_rules.c.v1).where(
            casbin_rules.c.ptype == "g",
            casbin_rules.c.v0.like("user:%"),
        )
    ).all()

    for subject, role in rows:
        user_id = int(subject.removeprefix("user:"))
        connection.execute(
            sa.update(users)
            .where(users.c.id == user_id)
            .values(role=role or "member")
        )

    connection.execute(
        sa.delete(casbin_rules).where(
            casbin_rules.c.ptype == "g",
            casbin_rules.c.v0.like("user:%"),
        )
    )
