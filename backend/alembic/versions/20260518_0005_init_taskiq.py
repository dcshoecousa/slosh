"""init taskiq

Revision ID: 20260518_0006
Revises: 20260518_0005
Create Date: 2026-05-18 17:51:35.981118
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '20260518_0006'
down_revision: str | None = '20260518_0005'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "taskiq_messages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("task_name", sa.String(), nullable=False),
        sa.Column("message", postgresql.BYTEA(), nullable=False),
        sa.Column("labels", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        if_not_exists=True,
    )
    op.create_index(
        "taskiq_messages_id_idx",
        "taskiq_messages",
        ["id"],
        unique=False,
        postgresql_using="hash",
        if_not_exists=True,
    )

    op.create_table(
        "taskiq_results",
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("result", postgresql.BYTEA(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        if_not_exists=True,
    )
    op.create_index(
        "taskiq_results_task_id_idx",
        "taskiq_results",
        ["task_id"],
        unique=False,
        postgresql_using="hash",
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "taskiq_results_task_id_idx",
        table_name="taskiq_results",
        if_exists=True,
    )
    op.drop_table("taskiq_results", if_exists=True)

    op.drop_index(
        "taskiq_messages_id_idx",
        table_name="taskiq_messages",
        if_exists=True,
    )
    op.drop_table("taskiq_messages", if_exists=True)

