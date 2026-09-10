"""add users table

Revision ID: 74a52d1d58cc
Revises: ef8aeaaae3ee
Create Date: 2026-09-10 11:22:53.552460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74a52d1d58cc'
down_revision: Union[str, Sequence[str], None] = 'ef8aeaaae3ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('id', existing_type=sa.INTEGER(), nullable=False, autoincrement=True)
        batch_op.alter_column('name', existing_type=sa.TEXT(), type_=sa.String(), existing_nullable=False)

    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.alter_column('id', existing_type=sa.INTEGER(), nullable=False, autoincrement=True)
        batch_op.alter_column('comment', existing_type=sa.TEXT(), type_=sa.String(), existing_nullable=True)
        batch_op.create_foreign_key('fk_reviews_recipe_id', 'recipes', ['recipe_id'], ['id'])

def downgrade() -> None:
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_constraint('fk_reviews_recipe_id', type_='foreignkey')
        batch_op.alter_column('comment', existing_type=sa.String(), type_=sa.TEXT(), existing_nullable=True)
        batch_op.alter_column('id', existing_type=sa.INTEGER(), nullable=True, autoincrement=True)

    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('name', existing_type=sa.String(), type_=sa.TEXT(), existing_nullable=False)
        batch_op.alter_column('id', existing_type=sa.INTEGER(), nullable=True, autoincrement=True)

    op.drop_table('users')