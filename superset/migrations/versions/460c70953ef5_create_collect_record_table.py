"""create collect record table

Revision ID: 460c70953ef5
Revises: 7bca6dd7d589
Create Date: 2018-08-02 18:23:07.987897

"""

# revision identifiers, used by Alembic.
revision = '460c70953ef5'
down_revision = '7bca6dd7d589'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collect_record',
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('changed_on', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('task_name', sa.String(length=50), nullable=False),
    sa.Column('is_success', sa.Boolean(), default=False, nullable=True),
    sa.Column('collect_rule_id', sa.Integer(), nullable=False),
    sa.Column('collect_rule_name', sa.String(length=60), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('created_by_fk', sa.Integer(), nullable=True),
    sa.Column('changed_by_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    )
    # op.create_unique_constraint(None, 'ab_permission_view', ['permission_id', 'view_menu_id'])
    # op.create_unique_constraint(None, 'ab_permission_view_role', ['permission_view_id', 'role_id'])
    # op.create_unique_constraint(None, 'ab_user_role', ['user_id', 'role_id'])
    # op.create_foreign_key(None, 'column_owners', 'table_columns', ['column_id'], ['id'])
    # op.create_foreign_key(None, 'column_owners', 'ab_user', ['user_id'], ['id'])
    # op.add_column('columns', sa.Column('datasource_id', sa.Integer(), nullable=True))
    # op.create_unique_constraint(None, 'columns', ['column_name', 'datasource_id'])
    # op.drop_constraint('columns_ibfk_3', 'columns', type_='foreignkey')
    # op.create_foreign_key(None, 'columns', 'datasources', ['datasource_id'], ['id'])
    # op.drop_column('columns', 'datasource_name')
    # op.drop_index('datasource_name', table_name='datasources')
    # op.create_unique_constraint(None, 'datasources', ['datasource_name', 'cluster_name'])
    # op.alter_column('m_element', 'del_status',
    #            existing_type=mysql.TINYINT(display_width=4),
    #            nullable=True,
    #            existing_server_default=sa.text("'0'"))
    # op.alter_column('m_element', 'status',
    #            existing_type=mysql.TINYINT(display_width=4),
    #            nullable=True,
    #            existing_server_default=sa.text("'0'"))
    # op.alter_column('m_page', 'del_status',
    #            existing_type=mysql.TINYINT(display_width=4),
    #            nullable=True,
    #            existing_server_default=sa.text("'0'"))
    # op.alter_column('m_page', 'status',
    #            existing_type=mysql.TINYINT(display_width=4),
    #            nullable=True,
    #            existing_server_default=sa.text("'0'"))
    # op.alter_column('m_project', 'status',
    #            existing_type=mysql.TINYINT(display_width=4),
    #            nullable=True,
    #            existing_server_default=sa.text("'0'"))
    # op.alter_column('melement_mpage_mproject', 'melement_id',
    #            existing_type=mysql.INTEGER(display_width=11),
    #            nullable=True)
    # op.alter_column('melement_mpage_mproject', 'mpage_mproject_id',
    #            existing_type=mysql.INTEGER(display_width=11),
    #            nullable=True)
    # op.create_foreign_key(None, 'melement_mpage_mproject', 'mpage_mproject', ['mpage_mproject_id'], ['id'])
    # op.create_foreign_key(None, 'melement_mpage_mproject', 'm_element', ['melement_id'], ['id'])
    # op.add_column('metrics', sa.Column('datasource_id', sa.Integer(), nullable=True))
    # op.add_column('metrics', sa.Column('warning_text', sa.Text(), nullable=True))
    # op.create_unique_constraint(None, 'metrics', ['metric_name', 'datasource_id'])
    # op.drop_constraint('metrics_ibfk_1', 'metrics', type_='foreignkey')
    # op.create_foreign_key(None, 'metrics', 'datasources', ['datasource_id'], ['id'])
    # op.drop_column('metrics', 'datasource_name')
    # op.drop_index('index_page', table_name='mpage_mproject')
    # op.drop_index('index_project', table_name='mpage_mproject')
    # op.create_foreign_key(None, 'mpage_mproject', 'm_page', ['mpage_id'], ['id'])
    # op.create_foreign_key(None, 'mpage_mproject', 'm_project', ['mproject_id'], ['id'])
    # op.create_unique_constraint(None, 'sql_metrics', ['table_id', 'metric_name'])
    # op.create_unique_constraint(None, 'table_columns', ['table_id', 'column_name'])
    # op.alter_column('tables', 'group_id',
    #            existing_type=mysql.INTEGER(display_width=11),
    #            nullable=False)
    # op.drop_index('_customer_location_uc', table_name='tables')
    # op.create_unique_constraint(None, 'tables', ['database_id', 'table_name'])
    # op.create_foreign_key(None, 'tables', 'tables_group', ['group_id'], ['id'])
    # op.alter_column('tables_group', 'name',
    #            existing_type=mysql.VARCHAR(length=64),
    #            nullable=False)
    # op.create_unique_constraint(None, 'tables_group', ['sort_id'])
    # op.create_unique_constraint(None, 'tables_group', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tables_group', type_='unique')
    op.drop_constraint(None, 'tables_group', type_='unique')
    op.alter_column('tables_group', 'name',
               existing_type=mysql.VARCHAR(length=64),
               nullable=True)
    op.drop_constraint(None, 'tables', type_='foreignkey')
    op.drop_constraint(None, 'tables', type_='unique')
    op.create_index('_customer_location_uc', 'tables', ['database_id', 'schema', 'table_name'], unique=True)
    op.alter_column('tables', 'group_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.drop_constraint(None, 'table_columns', type_='unique')
    op.drop_constraint(None, 'sql_metrics', type_='unique')
    op.drop_constraint(None, 'mpage_mproject', type_='foreignkey')
    op.drop_constraint(None, 'mpage_mproject', type_='foreignkey')
    op.create_index('index_project', 'mpage_mproject', ['mproject_id'], unique=False)
    op.create_index('index_page', 'mpage_mproject', ['mpage_id'], unique=False)
    op.add_column('metrics', sa.Column('datasource_name', mysql.VARCHAR(length=255), nullable=True))
    op.drop_constraint(None, 'metrics', type_='foreignkey')
    op.create_foreign_key('metrics_ibfk_1', 'metrics', 'datasources', ['datasource_name'], ['datasource_name'])
    op.drop_constraint(None, 'metrics', type_='unique')
    op.drop_column('metrics', 'warning_text')
    op.drop_column('metrics', 'datasource_id')
    op.drop_constraint(None, 'melement_mpage_mproject', type_='foreignkey')
    op.drop_constraint(None, 'melement_mpage_mproject', type_='foreignkey')
    op.alter_column('melement_mpage_mproject', 'mpage_mproject_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('melement_mpage_mproject', 'melement_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('m_project', 'status',
               existing_type=mysql.TINYINT(display_width=4),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.alter_column('m_page', 'status',
               existing_type=mysql.TINYINT(display_width=4),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.alter_column('m_page', 'del_status',
               existing_type=mysql.TINYINT(display_width=4),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.alter_column('m_element', 'status',
               existing_type=mysql.TINYINT(display_width=4),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.alter_column('m_element', 'del_status',
               existing_type=mysql.TINYINT(display_width=4),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.drop_constraint(None, 'datasources', type_='unique')
    op.create_index('datasource_name', 'datasources', ['datasource_name'], unique=True)
    op.add_column('columns', sa.Column('datasource_name', mysql.VARCHAR(length=255), nullable=True))
    op.drop_constraint(None, 'columns', type_='foreignkey')
    op.create_foreign_key('columns_ibfk_3', 'columns', 'datasources', ['datasource_name'], ['datasource_name'])
    op.drop_constraint(None, 'columns', type_='unique')
    op.drop_column('columns', 'datasource_id')
    op.drop_constraint(None, 'column_owners', type_='foreignkey')
    op.drop_constraint(None, 'column_owners', type_='foreignkey')
    op.drop_constraint(None, 'ab_user_role', type_='unique')
    op.drop_constraint(None, 'ab_permission_view_role', type_='unique')
    op.drop_constraint(None, 'ab_permission_view', type_='unique')
    # ### end Alembic commands ###
