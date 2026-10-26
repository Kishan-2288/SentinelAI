"""add test case review fields

Revision ID: e7184c446aaf
Revises: ba6ea6d53088
Create Date: 2026-10-18 22:34:48.197528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7184c446aaf'
down_revision: Union[str, Sequence[str], None] = 'ba6ea6d53088'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("test_case_results") as batch_op:
        batch_op.add_column(
            sa.Column("outcome_reason", sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("reviewer_outcome", sa.String(length=30), nullable=True)
        )
        batch_op.add_column(
            sa.Column("reviewer_note", sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("test_case_results") as batch_op:
        batch_op.drop_column("reviewed_at")
        batch_op.drop_column("reviewer_note")
        batch_op.drop_column("reviewer_outcome")
        batch_op.drop_column("outcome_reason")
