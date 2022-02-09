import pytest
import requests
import time


credentials = {
    "login": "test_user",
    "email": "test_email@mail.com",
    "password": "pass123",
}

credentials_user_for_tests = {
    "login": "test_user_for_tests",
    "email": "test_email@yaboo.com",
    "password": "pass12345",
}


@pytest.fixture(scope="session")
def base_url():
    return "http://81.163.25.103:5000/api/v1"


@pytest.fixture(scope="session")
def login_endpoint(base_url):
    resource = "/login"
    endpoint = f"{base_url}{resource}"
    return endpoint


@pytest.fixture(scope="session")
def register_endpoint(base_url):
    resource = "/register"
    endpoint = f"{base_url}{resource}"
    return endpoint


@pytest.fixture(scope="session")
def me_endpoint(base_url):
    resource = "/me"
    endpoint = f"{base_url}{resource}"
    return endpoint


@pytest.fixture(scope="session")
def role_endpoint():
    resource = "/roles"
    role_id = "9ee16219-488d-4237-857d-54a3be226702"
    endpoint = f"{base_url}{resource}"
    if role_id:
        endpoint = f"{endpoint}/{role_id}"
    return endpoint


@pytest.fixture(scope="session")
def token(login_endpoint):
    r = requests.post(login_endpoint, params=credentials)
    data = r.json()
    return data


@pytest.fixture(scope="session")
def admin_header(login_endpoint):
    r = requests.post(login_endpoint, params=credentials)
    data = r.json()
    admin_header = {"Authorization": f"Bearer {data['access_token']}"}
    return admin_header


@pytest.fixture(scope="session")
def not_admin_header(login_endpoint):
    r = requests.post(login_endpoint, params=credentials_user_for_tests)
    data = r.json()
    admin_header = {"Authorization": f"Bearer {data['access_token']}"}
    return admin_header


def test_register(register_endpoint):
    r = requests.post(register_endpoint, params=credentials_user_for_tests)
    assert r.status_code in (201, 400)


def test_me(admin_header, me_endpoint):
    r = requests.get(me_endpoint, headers=admin_header)
    assert r.status_code == 200
    assert r.json()["login"] == "test_user"


class TestRole:
    @pytest.fixture(scope="class")
    def endpoint_url(self):
        return "http://81.163.25.103:5000/api/v1/roles"

    @pytest.fixture(scope="class")
    def role_id(self):
        return "/9ee16219-488d-4237-857d-54a3be226702"

    def test_create_role(self, admin_header, endpoint_url):
        params = {"name": "bar", "description": f"{time.time()}: Bar role"}
        r = requests.post(endpoint_url, params=params, headers=admin_header)
        assert r.status_code == 201

    def test_get_role_by_id(self, admin_header, endpoint_url, role_id):
        r = requests.get(endpoint_url + role_id, headers=admin_header)
        assert r.status_code == 200

    def test_get_all_roles(self, admin_header, endpoint_url):
        r = requests.get(endpoint_url, headers=admin_header)
        print(r.json())
        assert r.status_code == 200

    def test_change_role_description_by_id(self, admin_header, endpoint_url, role_id):
        params = {
            "name": "foo",
            "description": f"{time.time()}: Changed description by id",
        }
        requests.patch(endpoint_url + role_id, params=params, headers=admin_header)
        r = requests.get(endpoint_url + role_id, headers=admin_header)
        assert r.json()["description"] == params.get("description")

    def test_delete_role_by_id(self, admin_header, endpoint_url):

        # find role_id by name 'bar'
        all_roles = requests.get(endpoint_url, headers=admin_header)
        id_to_delete = all_roles.json().get("bar").get("id")
        assert isinstance(id_to_delete, str)

        r = requests.delete(f"{endpoint_url}/{id_to_delete}", headers=admin_header)
        print(r.text)
        assert r.status_code == 204


class TestAssignRole:
    @pytest.fixture(scope="class")
    def endpoint_url(self):
        return "http://81.163.25.103:5000/api/v1/assign_role"

    def test_asign_role(self, admin_header, endpoint_url):
        print(endpoint_url)
        params = {
            "login": "test_user_for_tests",
            "name": "foo",
        }

        # Remove previouly assigned role
        requests.delete(endpoint_url, params=params, headers=admin_header)
        r = requests.post(endpoint_url, params=params, headers=admin_header)
        print(r.json())
        assert r.status_code == 200

    def test_remove_role(self, admin_header, endpoint_url):
        params = {
            "login": "test_user_for_tests",
            "name": "foo",
        }
        r = requests.delete(endpoint_url, params=params, headers=admin_header)
        assert r.status_code == 200

    def test_assign_role_without_admin_role(self, not_admin_header, endpoint_url):
        params = {
            "login": "test_user_for_tests",
            "name": "foo",
        }
        r = requests.delete(endpoint_url, params=params, headers=not_admin_header)
        print(r.json())
        assert r.status_code == 403

    def test_asign_same_role_twice(self, admin_header, endpoint_url):
        params = {
            "login": "test_user_for_tests",
            "name": "foo",
        }
        # Remove previouly assigned role
        requests.delete(endpoint_url, params=params, headers=admin_header)
        requests.post(endpoint_url, params=params, headers=admin_header)
        r2 = requests.post(endpoint_url, params=params, headers=admin_header)
        print(r2.json())
