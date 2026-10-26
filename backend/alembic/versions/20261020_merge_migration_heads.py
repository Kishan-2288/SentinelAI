"""Merge the findings payload and retest/review migration branches."""

from typing import Sequence, Union


revision: str = "20261020_merge_heads"
down_revision: Union[tuple[str, str], None] = (
    "4248a4312a33",
    "20261020_retest_review",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
