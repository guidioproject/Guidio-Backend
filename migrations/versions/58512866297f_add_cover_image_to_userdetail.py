"""add cover_image to UserDetail

Revision ID: 58512866297f
Revises: 3ce8d8121b20
Create Date: 2023-03-24 21:53:38.484991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58512866297f'
down_revision = '3ce8d8121b20'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_detail', sa.Column('cover_image', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_detail', 'cover_image')
    # ### end Alembic commands ###
