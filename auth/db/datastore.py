from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore

from .db_models import User, Role
from db import db

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()


def init_datastore(app: Flask):
    security.init_app(app, user_datastore)
