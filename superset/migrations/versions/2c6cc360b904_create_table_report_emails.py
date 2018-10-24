"""create table report emails

Revision ID: 2c6cc360b904
Revises: eb012314acb0
Create Date: 2018-10-24 14:10:04.337990

"""

# revision identifiers, used by Alembic.
revision = '2c6cc360b904'
down_revision = 'eb012314acb0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('annotation_layer',
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('changed_on', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=True),
    sa.Column('descr', sa.Text(), nullable=True),
    sa.Column('created_by_fk', sa.Integer(), nullable=True),
    sa.Column('changed_by_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('annotation',
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('changed_on', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_dttm', sa.DateTime(), nullable=True),
    sa.Column('end_dttm', sa.DateTime(), nullable=True),
    sa.Column('layer_id', sa.Integer(), nullable=True),
    sa.Column('short_descr', sa.String(length=500), nullable=True),
    sa.Column('long_descr', sa.Text(), nullable=True),
    sa.Column('created_by_fk', sa.Integer(), nullable=True),
    sa.Column('changed_by_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['layer_id'], ['annotation_layer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ti_dag_state', 'annotation', ['layer_id', 'start_dttm', 'end_dttm'], unique=False)
    op.create_table('dashboard_email_schedules',
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('changed_on', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('crontab', sa.String(length=50), nullable=True),
    sa.Column('recipients', sa.Text(), nullable=True),
    sa.Column('deliver_as_group', sa.Boolean(), nullable=True),
    sa.Column('delivery_type', sa.Enum('attachment', 'inline', name='emaildeliverytype'), nullable=True),
    sa.Column('dashboard_id', sa.Integer(), nullable=True),
    sa.Column('created_by_fk', sa.Integer(), nullable=True),
    sa.Column('changed_by_fk', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dashboard_email_schedules_active'), 'dashboard_email_schedules', ['active'], unique=False)
    op.create_table('slice_email_schedules',
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('changed_on', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('crontab', sa.String(length=50), nullable=True),
    sa.Column('recipients', sa.Text(), nullable=True),
    sa.Column('deliver_as_group', sa.Boolean(), nullable=True),
    sa.Column('delivery_type', sa.Enum('attachment', 'inline', name='emaildeliverytype'), nullable=True),
    sa.Column('slice_id', sa.Integer(), nullable=True),
    sa.Column('email_format', sa.Enum('visualization', 'data', name='sliceemailreportformat'), nullable=True),
    sa.Column('created_by_fk', sa.Integer(), nullable=True),
    sa.Column('changed_by_fk', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['slice_id'], ['slices.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_slice_email_schedules_active'), 'slice_email_schedules', ['active'], unique=False)
    # op.drop_table('m_page_test')
    # op.drop_table('ab_permission_view_role_test')
    # op.drop_index('index_page', table_name='mpage_mproject_test')
    # op.drop_index('index_project', table_name='mpage_mproject_test')
    # op.drop_table('mpage_mproject_test')
    # op.drop_table('ab_user_role_copy')
    # op.create_unique_constraint(None, 'ab_permission_view', ['permission_id', 'view_menu_id'])
    # op.create_unique_constraint(None, 'ab_permission_view_role', ['permission_view_id', 'role_id'])
    # op.create_unique_constraint(None, 'ab_user_role', ['user_id', 'role_id'])
    # op.create_foreign_key(None, 'column_owners', 'ab_user', ['user_id'], ['id'])
    # op.create_foreign_key(None, 'column_owners', 'table_columns', ['column_id'], ['id'])
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
    # op.create_foreign_key(None, 'melement_mpage_mproject', 'm_element', ['melement_id'], ['id'])
    # op.create_foreign_key(None, 'melement_mpage_mproject', 'mpage_mproject', ['mpage_mproject_id'], ['id'])
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
    op.create_table('ab_user_role_copy',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('role_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['ab_role.id'], name='ab_user_role_copy_ibfk_2'),
    sa.ForeignKeyConstraint(['user_id'], ['ab_user.id'], name='ab_user_role_copy_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('mpage_mproject_test',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('mproject_id', mysql.VARCHAR(length=64), nullable=False),
    sa.Column('mpage_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_index('index_project', 'mpage_mproject_test', ['mproject_id'], unique=False)
    op.create_index('index_page', 'mpage_mproject_test', ['mpage_id'], unique=False)
    op.create_table('ab_permission_view_role_test',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('permission_view_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('role_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('m_page_test',
    sa.Column('id', mysql.INTEGER(display_width=64, unsigned=True), nullable=False),
    sa.Column('page_id', mysql.VARCHAR(length=64), nullable=False),
    sa.Column('menu1', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('menu2', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('menu3', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('menu4', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('name', mysql.VARCHAR(length=64), nullable=False),
    sa.Column('status', mysql.TINYINT(display_width=4), server_default=sa.text("'0'"), autoincrement=False, nullable=False),
    sa.Column('del_status', mysql.TINYINT(display_width=4), server_default=sa.text("'0'"), autoincrement=False, nullable=False),
    sa.Column('url', mysql.VARCHAR(length=2048), nullable=True),
    sa.Column('m_describe', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('up1', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('up2', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('up3', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('up4', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('up5', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('pp1', mysql.VARCHAR(length=2048), nullable=True),
    sa.Column('pp2', mysql.VARCHAR(length=2048), nullable=True),
    sa.Column('pp3', mysql.VARCHAR(length=2048), nullable=True),
    sa.Column('pp4', mysql.VARCHAR(length=2048), nullable=True),
    sa.Column('pp5', mysql.VARCHAR(length=2048), nullable=True),
    sa.Column('tag', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('m_process', mysql.TINYINT(display_width=4), server_default=sa.text("'1'"), autoincrement=False, nullable=False),
    sa.Column('version', mysql.SMALLINT(display_width=6), server_default=sa.text("'1'"), autoincrement=False, nullable=False),
    sa.Column('create_time', mysql.DATETIME(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('update_time', mysql.DATETIME(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('melement_url', mysql.VARCHAR(length=2048), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.drop_index(op.f('ix_slice_email_schedules_active'), table_name='slice_email_schedules')
    op.drop_table('slice_email_schedules')
    op.drop_index(op.f('ix_dashboard_email_schedules_active'), table_name='dashboard_email_schedules')
    op.drop_table('dashboard_email_schedules')
    op.drop_index('ti_dag_state', table_name='annotation')
    op.drop_table('annotation')
    op.drop_table('annotation_layer')
    # ### end Alembic commands ###
