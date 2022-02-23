from http import HTTPStatus

from db.db_models import User


def test_login_is_ok(client, default_user, default_login, default_password):
    response = client.post(path="/admin/login",
                           data={
                               "login": default_login,
                               "password": default_password,
                           })

    assert response.status_code == HTTPStatus.OK
    assert response.json.get("access_token") and response.json.get("refresh_token")


def test_login_is_wrong(client):
    response = client.post(path="/admin/login",
                           data={
                               "login": "wrong_login",
                               "password": "wrong_password",
                           })
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_register_is_ok(client):
    login = "new_user"
    password = "password"
    email = "user@gmail.com"

    response = client.post(path="/admin/register",
                           data={
                               "login": login,
                               "password": password,
                               "email": email
                           })

    assert response.status_code == HTTPStatus.CREATED
    user = User.query.filter_by(login=login).one_or_none()
    assert user and user.email == email and user.check_password(password)


def test_register_with_existing_login(client, default_login):
    response = client.post(path="/admin/register",
                           data={
                               "login": default_login,
                               "password": "password",
                               "email": "someemail@mail.ru"
                           })

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json.get('message') == 'User with current login or email already exists'


def test_register_with_existing_email(client, default_email):
    response = client.post(path="/admin/register",
                           data={
                               "login": "new_user_login",
                               "password": "password",
                               "email": default_email
                           })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json.get('message') == 'User with current login or email already exists'


def test_logout_ok(client, access_token_for_default_user):
    response = client.post(path="/admin/logout",
                           headers=access_token_for_default_user)
    assert response.status_code == HTTPStatus.OK
    assert response.json.get('message') == 'Access token revoked'


def test_logout_with_refresh_token(client, refresh_token_for_default_user):
    response = client.post(path="/admin/logout",
                           headers=refresh_token_for_default_user)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json.get('msg') == 'Only non-refresh tokens are allowed'


def test_refresh_is_ok(client, refresh_token_for_default_user):
    response = client.post(path="/admin/refresh",
                           headers=refresh_token_for_default_user)

    assert response.status_code == HTTPStatus.OK
    assert response.json.get("access_token") and response.json.get("refresh_token")


def test_refresh_with_revoked_token(client, refresh_token_for_default_user):
    response = client.post(path="/admin/refresh",
                           headers=refresh_token_for_default_user)

    assert response.status_code == HTTPStatus.OK
    response_new = client.post(path="/admin/refresh",
                               headers=refresh_token_for_default_user)
    assert response_new.status_code == HTTPStatus.BAD_REQUEST
    assert response_new.json.get("message") == "Wrong refresh token"


def test_refresh_with_new_token(client, refresh_token_for_default_user):
    response = client.post(path="/admin/refresh",
                           headers=refresh_token_for_default_user)

    assert response.status_code == HTTPStatus.OK
    token = response.json.get("refresh_token")
    response_new = client.post(path="/admin/refresh",
                               headers={"Authorization": f"Bearer {token}"})
    assert response_new.status_code == HTTPStatus.OK
    assert response_new.json.get("access_token") and response_new.json.get("refresh_token")


def test_password_change_is_ok(client, access_token_for_default_user, default_password, default_user):
    new_password = "new_password"
    response = client.post(path="/admin/password-change",
                           headers=access_token_for_default_user,
                           data={
                               "current_password": default_password,
                               "new_password": new_password
                           })
    assert response.status_code == HTTPStatus.OK
    assert response.json.get("message") == "Password successfully changed, please login again"
    assert default_user.check_password(new_password)
