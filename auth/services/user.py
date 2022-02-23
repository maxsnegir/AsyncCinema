from typing import Optional
from uuid import uuid4

from werkzeug.security import generate_password_hash

from db import db_session
from db.datastore import user_datastore
from db.db_models import User, DefaultRoles


class UserService:

    @classmethod
    def get_user_by_login(cls, login: str):
        """Получение пользователя по логину"""

        user = User.query.filter_by(login=login).one_or_none()
        return user

    @classmethod
    def create_user(cls, login: str, email: str, password: str = None, role_name: str = None):
        """Создание пользователя"""

        password = generate_password_hash(password or str(uuid4()))
        role_name = role_name or DefaultRoles.USER

        try:
            with db_session():
                user = user_datastore.create_user(login=login,
                                                  password=password,
                                                  email=email)
                user_datastore.add_role_to_user(user, role_name)
        except Exception as ex:
            raise ex

        return user

    @classmethod
    def get_or_create(cls, login: str, email: str, password: Optional[str] = None,
                      role_name: Optional[str] = None):
        """Получить пользователя по логину или создать"""

        user = cls.get_user_by_login(login)
        if not user:
            try:
                user = cls.create_user(login, email, password, role_name)
            except Exception as ex:
                raise ex
        return user
