from flask_appbuilder.security.views import UserDBModelView
from flask_babel import lazy_gettext

class MyUserDBModelView(UserDBModelView):
    """
        View that add DB specifics to User view.
        Override to implement your own custom view.
        Then override userdbmodelview property on SecurityManager
    """
    new_label=UserDBModelView.label_columns
    new_label['department']='部门'
    label_columns=new_label
    show_fieldsets = [
        (lazy_gettext('User info'),
         {'fields': ['username', 'active', 'roles', 'login_count', 'department']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
        (lazy_gettext('Audit Info'),
         {'fields': ['last_login', 'fail_login_count', 'created_on',
                     'created_by', 'changed_on', 'changed_by'], 'expanded': False}),
    ]

    user_show_fieldsets = [
        (lazy_gettext('User info'),
         {'fields': ['username', 'active', 'roles', 'login_count', 'department']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
    ]

    add_columns = [ 'last_name','first_name', 'department','username', 'active', 'email', 'roles',  'password', 'conf_password']
    list_columns = [ 'last_name','first_name','department', 'username', 'email', 'active', 'roles']
    edit_columns = ['last_name','first_name',  'department', 'username', 'active', 'email', 'roles']