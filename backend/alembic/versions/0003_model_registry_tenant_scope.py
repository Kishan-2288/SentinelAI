"""Add tenant ownership to model configurations.

Revision ID: 0003
Revises: 0001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("model_configs") as batch_op:
        batch_op.add_column(sa.Column("owner_id", sa.String(length=64), nullable=True))
        batch_op.drop_constraint("uq_model_configs_provider_model", type_="unique")
        batch_op.create_unique_constraint(
            "uq_model_configs_owner_provider_model", ["owner_id", "provider", "model"]
        )
        batch_op.create_index("ix_model_configs_owner_id", ["owner_id"], unique=False)

    op.execute(sa.text("UPDATE model_configs SET owner_id = 'local-dev' WHERE owner_id IS NULL"))
    with op.batch_alter_table("model_configs") as batch_op:
        batch_op.alter_column("owner_id", existing_type=sa.String(length=64), nullable=False)

    # Older deployments used a non-null `created_at` column on audit_events.
    # The hash-chain schema writes `occurred_at`; retain the legacy column for
    # compatibility, but make it optional so new audit events can be inserted.
    inspector = sa.inspect(op.get_bind())
    audit_columns = {column["name"]: column for column in inspector.get_columns("audit_events")}
    if "created_at" in audit_columns:
        with op.batch_alter_table("audit_events") as batch_op:
            batch_op.alter_column(
                "created_at",
                existing_type=audit_columns["created_at"]["type"],
                nullable=True,
            )


def downgrade() -> None:
    with op.batch_alter_table("model_configs") as batch_op:
        batch_op.drop_index("ix_model_configs_owner_id")
        batch_op.drop_constraint("uq_model_configs_owner_provider_model", type_="unique")
        batch_op.create_unique_constraint(
            "uq_model_configs_provider_model", ["provider", "model"]
        )
        batch_op.drop_column("owner_id")
