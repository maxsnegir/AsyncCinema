from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

from api import api
from db.db_models import User

jwt_manager = JWTManager()
jwt_manager._set_error_handler_callbacks(api)


@jwt_manager.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Функция определяет пользователя по токену"""

    identity = jwt_data["sub"]
    user = User.query.filter_by(id=identity).one_or_none()
    return user


def init_jwt(app: Flask):
    app.config["JWT_SECRET_KEY"] = "super-secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=1)
    jwt_manager.init_app(app)
