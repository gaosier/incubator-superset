"""create monitor tables

Revision ID: e6979f6d1e3f
Revises: f231d82b9b26
Create Date: 2018-08-02 16:41:00.790128

"""

# revision identifiers, used by Alembic.
revision = 'e6979f6d1e3f'
down_revision = 'f231d82b9b26'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jingyou_user',
    sa.Column('uname', sa.String(length=64), nullable=False),
    sa.Column('password', sa.String(length=64), nullable=True),
    sa.Column('ua', sa.Text(), nullable=True),
    sa.Column('cookies', sa.Text(), nullable=True),
    sa.Column('ip', sa.String(length=64), nullable=True),
    sa.Column('port', sa.SmallInteger(), nullable=True),
    sa.Column('comment', sa.String(length=255), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('status', sa.SmallInteger(), nullable=False),
    sa.Column('subject_product', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('uname')
    )
    op.create_table('m_element',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('element_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('del_status', sa.Boolean(), nullable=True),
    sa.Column('pp1', sa.String(length=1024), nullable=True),
    sa.Column('pp2', sa.String(length=1024), nullable=True),
    sa.Column('pp3', sa.String(length=1024), nullable=True),
    sa.Column('pp4', sa.String(length=1024), nullable=True),
    sa.Column('pp5', sa.String(length=1024), nullable=True),
    sa.Column('tag', sa.String(length=255), nullable=True),
    sa.Column('m_process', sa.Integer(), nullable=False),
    sa.Column('version', sa.SmallInteger(), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('m_page',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('page_id', sa.String(length=64), nullable=False),
    sa.Column('menu1', sa.String(length=64), nullable=True),
    sa.Column('menu2', sa.String(length=64), nullable=True),
    sa.Column('menu3', sa.String(length=64), nullable=True),
    sa.Column('menu4', sa.String(length=64), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('del_status', sa.Boolean(), nullable=True),
    sa.Column('url', sa.String(length=2048), nullable=True),
    sa.Column('m_describe', sa.String(length=255), nullable=True),
    sa.Column('up1', sa.String(length=1024), nullable=True),
    sa.Column('up2', sa.String(length=1024), nullable=True),
    sa.Column('up3', sa.String(length=1024), nullable=True),
    sa.Column('up4', sa.String(length=1024), nullable=True),
    sa.Column('up5', sa.String(length=1024), nullable=True),
    sa.Column('pp1', sa.String(length=1024), nullable=True),
    sa.Column('pp2', sa.String(length=1024), nullable=True),
    sa.Column('pp3', sa.String(length=1024), nullable=True),
    sa.Column('pp4', sa.String(length=1024), nullable=True),
    sa.Column('pp5', sa.String(length=1024), nullable=True),
    sa.Column('tag', sa.String(length=255), nullable=True),
    sa.Column('m_process', sa.Integer(), nullable=False),
    sa.Column('version', sa.SmallInteger(), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('melement_url', sa.String(length=2048), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('m_project',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('full_id', sa.String(length=64), nullable=True),
    sa.Column('m_describe', sa.String(length=255), nullable=True),
    sa.Column('pm_owner', sa.String(length=64), nullable=True),
    sa.Column('tech_owner', sa.String(length=64), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('name_type', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('table_column_sort',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('table_id', sa.Integer(), nullable=True),
    sa.Column('table_name', sa.String(length=64), nullable=True),
    sa.Column('expression', sa.Text(), nullable=True),
    sa.Column('remark', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tables_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('sort_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('sort_id')
    )
    op.create_table('data_origin_config',
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('changed_on', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pro_name', sa.String(length=50), nullable=True),
    sa.Column('db_name', sa.String(length=50), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_by_fk', sa.Integer(), nullable=True),
    sa.Column('changed_by_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('md_config',
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('changed_on', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pro_id', sa.String(length=20), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('range', sa.String(length=90), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_by_fk', sa.Integer(), nullable=True),
    sa.Column('changed_by_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mpage_mproject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mproject_id', sa.String(length=32), nullable=False),
    sa.Column('mpage_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['mpage_id'], ['m_page.id'], ),
    sa.ForeignKeyConstraint(['mproject_id'], ['m_project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dashboard_show_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('dashboard_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('melement_mpage_mproject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('melement_id', sa.Integer(), nullable=True),
    sa.Column('mpage_mproject_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['melement_id'], ['m_element.id'], ),
    sa.ForeignKeyConstraint(['mpage_mproject_id'], ['mpage_mproject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('slice_show_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('slice_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['slice_id'], ['slices.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('column_owners',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('column_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['column_id'], ['table_columns.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('dbs', sa.Column('is_hybrid', sa.Boolean(), nullable=True))
    op.create_unique_constraint(None, 'sql_metrics', ['table_id', 'metric_name'])
    op.add_column('table_columns', sa.Column('is_memcached', sa.Boolean(), nullable=True))
    op.add_column('table_columns', sa.Column('is_partition', sa.Boolean(), nullable=True))
    op.add_column('table_columns', sa.Column('order_number', sa.INTEGER(), nullable=True))
    op.add_column('table_columns', sa.Column('partition_expression', sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, 'table_columns', ['table_id', 'column_name'])
    op.add_column('tables', sa.Column('group_id', sa.Integer(), nullable=False))
    op.add_column('tables', sa.Column('has_special_sort_cols', sa.Boolean(), nullable=True))
    op.add_column('tables', sa.Column('verbose_name', sa.String(length=1024), nullable=True))
    # op.drop_index('_customer_location_uc', table_name='tables')
    op.create_unique_constraint(None, 'tables', ['database_id', 'table_name'])
    op.create_foreign_key(None, 'tables', 'tables_group', ['group_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tables', type_='foreignkey')
    op.drop_constraint(None, 'tables', type_='unique')
    op.create_index('_customer_location_uc', 'tables', ['database_id', 'schema', 'table_name'], unique=True)
    op.drop_column('tables', 'verbose_name')
    op.drop_column('tables', 'has_special_sort_cols')
    op.drop_column('tables', 'group_id')
    op.drop_constraint(None, 'table_columns', type_='unique')
    op.drop_column('table_columns', 'partition_expression')
    op.drop_column('table_columns', 'order_number')
    op.drop_column('table_columns', 'is_partition')
    op.drop_column('table_columns', 'is_memcached')
    op.drop_constraint(None, 'sql_metrics', type_='unique')
    op.drop_column('dbs', 'is_hybrid')
    op.drop_table('column_owners')
    op.drop_table('slice_show_user')
    op.drop_table('melement_mpage_mproject')
    op.drop_table('dashboard_show_user')
    op.drop_table('mpage_mproject')
    op.drop_table('md_config')
    op.drop_table('data_origin_config')
    op.drop_table('tables_group')
    op.drop_table('table_column_sort')
    op.drop_table('m_project')
    op.drop_table('m_page')
    op.drop_table('m_element')
    op.drop_table('jingyou_user')
    # ### end Alembic commands ###
