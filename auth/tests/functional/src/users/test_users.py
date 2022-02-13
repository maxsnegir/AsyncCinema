from http import HTTPStatus


def test_me_is_ok(client, default_user, access_token_for_default_user):
    response = client.get(path="/api/v1/me",
                          headers=access_token_for_default_user)
    assert response.status_code == HTTPStatus.OK
    data = response.json
    assert str(default_user.id) == data["id"] and default_user.login == data["login"] \
           and default_user.email == data["email"]


def test_me_unauthorized(client):
    response = client.get(path="/api/v1/me")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_me_change_is_ok(client, default_user, access_token_for_default_user):
    email = "newemail@yandex.ru"
    login = "new_login_for_test"
    response = client.post(path="/api/v1/me",
                           headers=access_token_for_default_user,
                           data={"email": email,
                                 "login": login})
    assert response.status_code == HTTPStatus.OK
    assert default_user.login == login and default_user.email == email


def test_me_change_with_existing_login(client, admin_login, access_token_for_default_user):
    response = client.post(path="/api/v1/me",
                           headers=access_token_for_default_user,
                           data={"login": admin_login})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json.get("message") == "Login or email already exists"


def test_me_change_with_existing_email(client, admin_email, access_token_for_default_user):
    response = client.post(path="/api/v1/me",
                           headers=access_token_for_default_user,
                           data={"email": "newemail@yandex.ru"})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json.get("message") == "Login or email already exists"


def test_auth_history(client, default_login, default_password, access_token_for_default_user):
    client.post(path="/admin/login", data={"login": default_login, "password": default_password})
    response = client.get(path="/api/v1/me/auth-history",
                          headers=access_token_for_default_user)

    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
