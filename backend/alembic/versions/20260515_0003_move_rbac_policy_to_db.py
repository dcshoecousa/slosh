"""move rbac policy to db

Revision ID: 20260515_0003
Revises: 20260515_0002
Create Date: 2026-05-15 16:30:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260515_0003"
down_revision: str | None = "20260515_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "casbin_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ptype", sa.String(length=16), nullable=False),
        sa.Column("v0", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("v1", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("v2", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("v3", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("v4", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("v5", sa.String(length=255), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ptype",
            "v0",
            "v1",
            "v2",
            "v3",
            "v4",
            "v5",
            name="uq_casbin_rules_policy",
        ),
    )
    op.create_index(op.f("ix_casbin_rules_id"), "casbin_rules", ["id"], unique=False)

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
    seed_rows = [
        ("p", "admin", "users", "create", "", "", ""),
        ("p", "admin", "users", "read", "", "", ""),
        ("p", "admin", "users", "update", "", "", ""),
        ("p", "admin", "users", "delete", "", "", ""),
        ("p", "admin", "auth", "read", "", "", ""),
        ("p", "admin", "rbac", "read", "", "", ""),
        ("p", "admin", "rbac", "check", "", "", ""),
        ("p", "admin", "rbac", "inspect", "", "", ""),
        ("p", "admin", "rbac", "assign_role", "", "", ""),
        ("p", "admin", "rbac", "revoke_role", "", "", ""),
        ("p", "admin", "rbac", "grant_permission", "", "", ""),
        ("p", "admin", "rbac", "revoke_permission", "", "", ""),
        ("p", "member", "auth", "read", "", "", ""),
        ("p", "member", "rbac", "read", "", "", ""),
        ("p", "member", "rbac", "check", "", "", ""),
        ("g", "admin", "admin", "", "", "", ""),
        ("g", "member", "member", "", "", "", ""),
    ]
    op.bulk_insert(
        casbin_rules,
        [
            {
                "ptype": ptype,
                "v0": v0,
                "v1": v1,
                "v2": v2,
                "v3": v3,
                "v4": v4,
                "v5": v5,
            }
            for ptype, v0, v1, v2, v3, v4, v5 in seed_rows
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_casbin_rules_id"), table_name="casbin_rules")
    op.drop_table("casbin_rules")
