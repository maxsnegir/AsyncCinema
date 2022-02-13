import pytest
from tests.functional.utils.user_helper import create_user

from db import db
from db.datastore import user_datastore
from db.db_models import DefaultRoles, Role
from main import app
from services.token import TokenService


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def init_db():
    db.create_all()
    for role in Role.Meta.BASE_ROLES:
        user_datastore.find_or_create_role(role)
    db.session.commit()
    yield
    db.session.close()
    db.drop_all()


@pytest.fixture
def role_name():
    return "New Role"


@pytest.fixture
def role_description():
    return "Role Description"


@pytest.fixture
def default_login():
    return "default_user"


@pytest.fixture
def default_password():
    return "default_password"


@pytest.fixture
def default_email():
    return "default_email@google.com"


@pytest.fixture
def admin_login():
    return "admin_user"


@pytest.fixture
def admin_password():
    return "admin_password"


@pytest.fixture
def admin_email():
    return "admin_email@google.com"


@pytest.fixture
def default_user(default_login, default_password, default_email):
    return create_user(default_login, default_email, default_password, DefaultRoles.USER)


@pytest.fixture
def admin_user(admin_login, admin_email, admin_password):
    return create_user(admin_login, admin_email, admin_password, DefaultRoles.ADMIN)


@pytest.fixture
def access_token_for_default_user(default_user):
    token_service = TokenService(default_user)
    access_token, _ = token_service.get_jwt_tokens()
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def refresh_token_for_default_user(default_user):
    token_service = TokenService(default_user)
    _, refresh_token = token_service.get_jwt_tokens()
    return {"Authorization": f"Bearer {refresh_token}"}


@pytest.fixture
def access_token_for_admin_user(admin_user):
    token_service = TokenService(admin_user)
    access_token, _ = token_service.get_jwt_tokens()
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def refresh_token_for_admin_user(admin_user):
    token_service = TokenService(admin_user)
    _, refresh_token = token_service.get_jwt_tokens()
    return {"Authorization": f"Bearer {refresh_token}"}
