"""add avatar to UserDetail model

Revision ID: 3ce8d8121b20
Revises: 78d7a665bd73
Create Date: 2023-03-24 12:00:21.773778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ce8d8121b20'
down_revision = '78d7a665bd73'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_detail', sa.Column('avatar', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_detail', 'avatar')
    # ### end Alembic commands ###
