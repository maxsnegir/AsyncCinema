from flask_restplus import Namespace

user_namespace = Namespace("Api v1", path="/api/v1", description="User actions")
from api.v1 import users, roles
