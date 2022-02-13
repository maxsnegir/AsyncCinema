from flask import Flask
from flask_jwt_extended import JWTManager

from api import api
from db.db_models import User
from settings import JWTSettings

jwt_manager = JWTManager()
jwt_manager._set_error_handler_callbacks(api)


@jwt_manager.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Функция определяет пользователя по токену"""

    identity = jwt_data["sub"]
    user = User.query.filter_by(id=identity).one_or_none()
    return user


def init_jwt(app: Flask):
    app.config["JWT_SECRET_KEY"] = JWTSettings().JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWTSettings().JWT_ACCESS_TOKEN_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = JWTSettings().JWT_REFRESH_TOKEN_EXPIRES
    jwt_manager.init_app(app)
