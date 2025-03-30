"""remove_station_id_from_cast_common_prof

Revision ID: fa5709e96d69
Revises: 89e7ae158b6d
Create Date: 2025-03-31 00:50:40.541420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa5709e96d69'
down_revision: Union[str, None] = '89e7ae158b6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # station_idu30abu30e9u30e0u304cu5b58u5728u3059u308bu5834u5408u306fu524au9664u3059u308b
    try:
        op.drop_column('cast_common_prof', 'station_id')
    except Exception as e:
        # u30abu30e9u30e0u304cu5b58u5728u3057u306au3044u5834u5408u306fu30a8u30e9u30fcu3092u7121u8996
        print(f"station_idu30abu30e9u30e0u306eu524au9664u4e2du306bu30a8u30e9u30fcu304cu767au751fu3057u307eu3057u305f: {e}")


def downgrade() -> None:
    """Downgrade schema."""
    # u524au9664u3057u305fu30abu30e9u30e0u3092u5143u306bu623bu3059u5fc5u8981u304cu3042u308bu5834u5408u306fu3053u3053u306bu8ffdu52a0
    pass
