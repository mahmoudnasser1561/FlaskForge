"""Add google_id to User model

Revision ID: d4e8a1f2c9b3
Revises: c1a9f3d7e5b2
Create Date: 2026-09-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e8a1f2c9b3'
down_revision = 'c1a9f3d7e5b2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('google_id', sa.String(length=64), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_google_id'), ['google_id'], unique=True)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_google_id'))
        batch_op.drop_column('google_id')
