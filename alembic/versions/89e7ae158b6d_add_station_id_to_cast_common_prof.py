"""add_station_id_to_cast_common_prof

Revision ID: 89e7ae158b6d
Revises: 00a79ef0dfd1
Create Date: 2025-03-31 00:45:44.586483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89e7ae158b6d'
down_revision: Union[str, None] = '00a79ef0dfd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # station_idカラムを追加しない
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # 何もしない
    pass
