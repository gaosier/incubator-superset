from flask_appbuilder.security.sqla.manager import SecurityManager
from superset.security import SupersetSecurityManager
from .sec_models import MyUser
from .sec_views import MyUserDBModelView

class MySecurityManager(SupersetSecurityManager):
    user_model = MyUser
    userdbmodelview = MyUserDBModelView