from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore

from db import db
from .db_models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()


def init_datastore(app: Flask):
    security.init_app(app, user_datastore)
