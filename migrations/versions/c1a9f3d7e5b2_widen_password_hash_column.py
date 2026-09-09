"""Widen password_hash column to fit scrypt hashes

Revision ID: c1a9f3d7e5b2
Revises: 8efbcd5a72db
Create Date: 2026-09-09 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1a9f3d7e5b2'
down_revision = '8efbcd5a72db'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
                               existing_type=sa.String(length=128),
                               type_=sa.String(length=255),
                               existing_nullable=True)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
                               existing_type=sa.String(length=255),
                               type_=sa.String(length=128),
                               existing_nullable=True)
