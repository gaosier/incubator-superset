"""add columns to validate_record

Revision ID: e08becb1b350
Revises: 051eecdf2029
Create Date: 2018-08-20 18:38:55.272264

"""

# revision identifiers, used by Alembic.
revision = 'e08becb1b350'
down_revision = '051eecdf2029'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('validate_record', sa.Column('operation', sa.String(length=60), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('validate_record', 'operation')
    # ### end Alembic commands ###