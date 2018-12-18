"""users table

Revision ID: 4b83761bf52a
Revises: 0d3bdf63aacc
Create Date: 2018-12-18 15:17:20.500426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b83761bf52a'
down_revision = '0d3bdf63aacc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('city', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('description', sa.String(length=256), nullable=True))
    op.add_column('user', sa.Column('phone', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'phone')
    op.drop_column('user', 'description')
    op.drop_column('user', 'city')
    # ### end Alembic commands ###
