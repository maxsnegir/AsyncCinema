from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from db import db_session
from db.datastore import user_datastore
from db.db_models import User


def create_user(login: str, email: str, password: str, role: str) -> User:
    try:
        with db_session():
            admin = user_datastore.create_user(login=login,
                                               password=generate_password_hash(password),
                                               email=email)
            user_datastore.add_role_to_user(admin, role)
    except IntegrityError:
        admin = User.get_user_by_login(login)
    return admin
