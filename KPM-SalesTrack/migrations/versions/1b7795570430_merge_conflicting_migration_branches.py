"""merge conflicting migration branches

Revision ID: 1b7795570430
Revises: 1c6c148379c1, 21a4c29934f5
Create Date: 2025-10-25 14:02:07.826839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b7795570430'
down_revision = ('1c6c148379c1', '21a4c29934f5')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
