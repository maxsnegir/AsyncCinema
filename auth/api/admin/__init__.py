from flask_restplus import Namespace

admin_namespace = Namespace("Api v1", path="admin", description="Auth actions")
from api.admin import users, roles
