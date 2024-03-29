"""userdetail fk to user nullable

Revision ID: 8935f6c89dd1
Revises: b197c53728fb
Create Date: 2023-04-04 13:23:13.121251

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8935f6c89dd1'
down_revision = 'b197c53728fb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_detail', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_detail', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
