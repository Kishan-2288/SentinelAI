"""Add missing test case result fields.

Revision ID: ba6ea6d53088
Revises: 0003
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ba6ea6d53088"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("test_case_results") as batch_op:
        batch_op.add_column(
            sa.Column("expected_answer", sa.String(length=500), nullable=True)
        )
        batch_op.add_column(
            sa.Column("forbidden_phrases", sa.JSON(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("test_case_results") as batch_op:
        batch_op.drop_column("forbidden_phrases")
        batch_op.drop_column("expected_answer")
