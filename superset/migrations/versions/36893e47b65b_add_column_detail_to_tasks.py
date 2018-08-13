"""add column detail to tasks

Revision ID: 36893e47b65b
Revises: 95c0b16791fb
Create Date: 2018-08-07 17:04:29.627218

"""

# revision identifiers, used by Alembic.
revision = '36893e47b65b'
down_revision = '95c0b16791fb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('detail', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'detail')
    # ### end Alembic commands ###