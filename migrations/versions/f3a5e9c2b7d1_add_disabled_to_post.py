"""Add disabled to Post model

Revision ID: f3a5e9c2b7d1
Revises: e7b2c4a1d6f8
Create Date: 2026-09-11 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3a5e9c2b7d1'
down_revision = 'e7b2c4a1d6f8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('disabled', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('disabled')
