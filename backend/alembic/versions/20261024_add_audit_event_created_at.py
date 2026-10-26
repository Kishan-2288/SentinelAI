"""Add audit_events.created_at (present on the AuditEvent model, missing from migrations).

created_at is not part of the hash chain (only occurred_at is hashed), so backfilling it
from occurred_at does not affect verification of existing events.
"""

from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


revision = "20261024_audit_created_at"
down_revision = "20261021_model_api_keys"
branch_labels = None
depends_on = None


def _parse(value) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def upgrade() -> None:
    bind = op.get_bind()
    columns = {c["name"] for c in sa.inspect(bind).get_columns("audit_events")}
    if "created_at" in columns:
        return
    with op.batch_alter_table("audit_events") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))

    events = sa.table(
        "audit_events",
        sa.column("id", sa.Integer),
        sa.column("occurred_at", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    for row_id, occurred_at in bind.execute(sa.select(events.c.id, events.c.occurred_at)).all():
        bind.execute(events.update().where(events.c.id == row_id).values(created_at=_parse(occurred_at)))

    with op.batch_alter_table("audit_events") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("audit_events") as batch_op:
        batch_op.drop_column("created_at")
