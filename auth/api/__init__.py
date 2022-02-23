from flask import Flask
from flask_restplus import Api

from api.admin import admin_namespace
from api.v1 import user_namespace

api = Api(
    title="Auth API",
    version="1.0",
    doc="/auth/doc"
)

api.add_namespace(admin_namespace)
api.add_namespace(user_namespace)


def init_api(app: Flask):
    api.init_app(app)
