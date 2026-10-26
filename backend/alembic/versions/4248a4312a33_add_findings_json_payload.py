"""add findings json payload

Revision ID: 4248a4312a33
Revises: e7184c446aaf
Create Date: 2026-10-18 22:45:03.546455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4248a4312a33'
down_revision: Union[str, Sequence[str], None] = 'e7184c446aaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("test_case_results")}
    if "findings" not in columns:
        with op.batch_alter_table("test_case_results") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "findings",
                    sa.JSON(),
                    nullable=False,
                    server_default=sa.text("'[]'"),
                )
            )
            batch_op.alter_column("findings", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("test_case_results") as batch_op:
        batch_op.drop_column("findings")
