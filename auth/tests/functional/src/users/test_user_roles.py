from http import HTTPStatus

from db.db_models import DefaultRoles, Role


def test_user_has_existing_role(client, admin_user, access_token_for_admin_user):
    role = Role.query.filter_by(name=DefaultRoles.ADMIN).one_or_none()
    response = client.get(path=f"/admin/{admin_user.id}/has-role/{role.id}",
                          headers=access_token_for_admin_user)
    assert response.status_code == HTTPStatus.OK
    has_role = role in admin_user.roles  # True
    assert response.json.get("has_role") == has_role


def test_user_has_non_existing_role(client, admin_user, access_token_for_admin_user):
    role = Role.query.filter_by(name=DefaultRoles.SUPER_USER).one_or_none()
    response = client.get(path=f"/admin/{admin_user.id}/has-role/{role.id}",
                          headers=access_token_for_admin_user)
    assert response.status_code == HTTPStatus.OK
    has_role = role in admin_user.roles  # False
    assert response.json.get("has_role") == has_role
