from http import HTTPStatus

from db.db_models import Role, DefaultRoles


def test_role_create_is_ok(client, access_token_for_admin_user, role_name, role_description):
    response = client.post(path="/admin/roles",
                           data={
                               "name": role_name,
                               "description": role_description,
                           },
                           headers=access_token_for_admin_user)
    assert response.status_code == HTTPStatus.CREATED
    role = Role.query.filter_by(name="New Role").one_or_none()
    assert role and role.name == role_name and role.description == role_description


def test_role_create_by_default_user(client, access_token_for_default_user, role_name, role_description):
    response = client.post(path="/admin/roles",
                           data={
                               "name": role_name,
                               "description": role_description,
                           },
                           headers=access_token_for_default_user)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json.get("message") == "Admins only!"


def test_create_existing_role(client, access_token_for_admin_user, role_name, role_description):
    response = client.post(path="/admin/roles",
                           data={
                               "name": role_name,
                               "description": role_description,
                           },
                           headers=access_token_for_admin_user)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json.get("message") == "Role already exists"


def test_role_create_without_auth(client, role_name, role_description):
    response = client.post(path="/admin/roles",
                           data={
                               "name": role_name,
                               "description": role_description,
                           })
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_roles_is_ok(client, access_token_for_admin_user):
    response = client.get(path="/admin/roles",
                          headers=access_token_for_admin_user)

    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 4


def test_get_roles_by_default_user(client, access_token_for_default_user):
    response = client.get(path="/admin/roles",
                          headers=access_token_for_default_user)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json.get("message") == "Admins only!"


def test_get_roles_without_auth(client):
    response = client.get(path="/admin/roles")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_change_role_is_ok(client, role_name, access_token_for_admin_user):
    role = Role.query.filter_by(name=role_name).one_or_none()
    new_name = "Role Name 2"
    new_description = "Role Description 2"
    response = client.patch(path=f"admin/roles/{str(role.id)}",
                            headers=access_token_for_admin_user,
                            data={"name": new_name,
                                  "description": new_description})

    assert response.status_code == HTTPStatus.OK
    assert role.name == new_name and role.description == new_description


def test_change_base_role_name(client, access_token_for_admin_user):
    role = Role.query.filter_by(name=DefaultRoles.ADMIN).one_or_none()
    response = client.patch(path=f"admin/roles/{str(role.id)}",
                            headers=access_token_for_admin_user,
                            data={"name": role.name,
                                  "description": ''})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json.get("message") == "You cant change base role names"


def test_delete_role(client, access_token_for_admin_user):
    role = Role.query.filter_by(name="Role Name 2").one_or_none()
    response = client.delete(path=f"admin/roles/{str(role.id)}",
                             headers=access_token_for_admin_user)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert Role.query.filter_by(name="Role Name 2").one_or_none() is None


def test_delete_base_role(client, access_token_for_admin_user):
    role = Role.query.filter_by(name=DefaultRoles.ADMIN).one_or_none()
    response = client.delete(path=f"admin/roles/{str(role.id)}",
                             headers=access_token_for_admin_user)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json.get("message") == "You can't delete base roles"


def test_assign_role_to_user(client, default_user, access_token_for_admin_user):
    role = Role.query.filter_by(name=DefaultRoles.ADMIN).one_or_none()
    response = client.post(path=f"admin/{default_user.id}/assign-role/{role.id}",
                           headers=access_token_for_admin_user)

    assert response.status_code == HTTPStatus.CREATED
    assert role in default_user.roles


def test_assign_existing_role_to_user(client, admin_user, access_token_for_admin_user):
    role = Role.query.filter_by(name=DefaultRoles.ADMIN).one_or_none()
    response = client.post(path=f"admin/{admin_user.id}/assign-role/{role.id}",
                           headers=access_token_for_admin_user)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json.get("message") == "Role already assigned"


def test_take_away_role(client, default_user, access_token_for_admin_user):
    role = Role.query.filter_by(name=DefaultRoles.ADMIN).one_or_none()
    response = client.delete(path=f"admin/{default_user.id}/assign-role/{role.id}",
                             headers=access_token_for_admin_user)

    assert response.status_code == HTTPStatus.OK
    assert role not in default_user.roles


def test_take_away_non_existing_role(client, default_user, access_token_for_admin_user):
    role = Role.query.filter_by(name=DefaultRoles.ADMIN).one_or_none()
    response = client.delete(path=f"admin/{default_user.id}/assign-role/{role.id}",
                             headers=access_token_for_admin_user)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json.get("message") == "User hasn't current role"
