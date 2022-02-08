import requests
import pytest

url = 'http://81.163.25.103:5000' # The root of the flask app
prefix = '/api/v1'

credentials = {
    "login": "test_user",
    "email": "test_email@mail.com",
    "password": "pass123"
}

credentials_user_for_tests = {
    "login": "test_user_for_tests",
    "email": "test_email@yaboo.com",
    "password": "pass12345"
}


@pytest.fixture(scope='session')
def token():
    r = requests.post(url+'/api/v1/login', params=credentials)
    data = r.json()
    return data

@pytest.fixture(scope='session')
def admin_auth_header():
    r = requests.post(url+'/api/v1/login', params=credentials)
    data = r.json()
    admin_auth_header = {"Authorization": f"Bearer {data['access_token']}"}
    return admin_auth_header


def test_register():
    endpoint = '/register'
    r = requests.post(url+prefix+endpoint, params=credentials_user_for_tests)
    assert r.status_code in (201, 400)


def test_me(token):
    endpoint = '/me'
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    r = requests.get(url+prefix+endpoint, params=credentials, headers=headers)
    assert r.status_code == 200
    assert r.json()['login'] == 'test_user'


def test_admin(token):
    endpoint = '/admin'
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    r = requests.get(url+prefix+endpoint, params=credentials, headers=headers)
    assert r.status_code == 200


def test_create_admin_role(admin_auth_header):
    endpoint = '/role'
    params = {'name':'admin', 'description':'administrator'}
    r = requests.post(url+prefix+endpoint, params=params, headers=admin_auth_header)
    #assert r.status_code == 200
    assert r.status_code == 400 #already exists


def test_asign_role(admin_auth_header):
    params = {
        "login": "test_user_for_tests",
        "name": "foo",
    }
    endpoint = '/assign_role'

    # Remove previouly assigned role
    requests.delete(url+prefix+endpoint, params=params, headers=admin_auth_header)

    r = requests.post(url+prefix+endpoint, params=params, headers=admin_auth_header)
    print(r.json())
    assert r.status_code==200


def test_remove_admin_role(admin_auth_header):
    params = {
        "login": "test_user_for_tests",
        "name": "foo",
    }
    endpoint = '/assign_role'
    r = requests.delete(url+prefix+endpoint, params=params, headers=admin_auth_header)
    assert r.status_code==200


def test_asign_same_role_twice(admin_auth_header):
    params = {
        "login": "test_user_for_tests",
        "name": "foo",
    }
    endpoint = '/assign_role'

    # Remove previouly assigned role
    requests.delete(url+prefix+endpoint, params=params, headers=admin_auth_header)

    requests.post(url+prefix+endpoint, params=params, headers=admin_auth_header)
    r2 = requests.post(url+prefix+endpoint, params=params, headers=admin_auth_header)
    print(r2.json())
    assert r2.status_code==400


def test_get_role(admin_auth_header):
    endpoint = '/role'
    r = requests.get(url+prefix+endpoint, headers=admin_auth_header)
    assert ('admin' in r.json().get('roles'))



