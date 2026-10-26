"""Add a field for encrypted provider API keys."""

from alembic import op
import sqlalchemy as sa


revision = "20261021_model_api_keys"
down_revision = "20261020_merge_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("model_configs") as batch_op:
        batch_op.add_column(sa.Column("encrypted_secret", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("model_configs") as batch_op:
        batch_op.drop_column("encrypted_secret")
