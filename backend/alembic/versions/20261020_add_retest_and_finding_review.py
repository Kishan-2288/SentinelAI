"""Add retest links and finding review metadata."""

from alembic import op
import sqlalchemy as sa


revision = "20261020_retest_review"
down_revision = "e7184c446aaf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("test_runs") as batch_op:
        batch_op.add_column(sa.Column("parent_run_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_test_runs_parent_run_id", ["parent_run_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_test_runs_parent_run_id", "test_runs", ["parent_run_id"], ["id"], ondelete="SET NULL"
        )
    with op.batch_alter_table("findings") as batch_op:
        batch_op.add_column(sa.Column("review_outcome", sa.String(length=30), nullable=False, server_default="unreviewed"))
        batch_op.add_column(sa.Column("reviewer_notes", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("findings") as batch_op:
        batch_op.drop_column("reviewed_at")
        batch_op.drop_column("reviewer_notes")
        batch_op.drop_column("review_outcome")
    with op.batch_alter_table("test_runs") as batch_op:
        batch_op.drop_constraint("fk_test_runs_parent_run_id", type_="foreignkey")
        batch_op.drop_index("ix_test_runs_parent_run_id")
        batch_op.drop_column("parent_run_id")
