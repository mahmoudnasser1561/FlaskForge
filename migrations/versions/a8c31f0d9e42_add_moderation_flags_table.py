"""Add moderation_flags table

Revision ID: a8c31f0d9e42
Revises: f3a5e9c2b7d1
Create Date: 2026-09-12 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8c31f0d9e42'
down_revision = 'f3a5e9c2b7d1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('moderation_flags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('comment_id', sa.Integer(), nullable=True),
    sa.Column('source', sa.String(length=16), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('moderator_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('overturned_at', sa.DateTime(), nullable=True),
    sa.Column('overturned_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
    sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['overturned_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('moderation_flags', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_moderation_flags_user_id'), ['user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_moderation_flags_timestamp'), ['timestamp'], unique=False)


def downgrade():
    with op.batch_alter_table('moderation_flags', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_moderation_flags_timestamp'))
        batch_op.drop_index(batch_op.f('ix_moderation_flags_user_id'))

    op.drop_table('moderation_flags')
