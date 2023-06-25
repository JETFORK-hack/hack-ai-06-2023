"""file update

Revision ID: ff36be93147d
Revises: b48a1cb7c15f
Create Date: 2023-06-24 17:03:32.830349

"""
from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision = 'ff36be93147d'
down_revision = 'b48a1cb7c15f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('name', sa.String(), nullable=True))
    op.add_column('files', sa.Column('size', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('files', 'size')
    op.drop_column('files', 'name')
    # ### end Alembic commands ###
