import requests
import pytest
#api_v1 = Api(prefix="/api/v1")
#api_v1.add_resource(UserRegister, '/register')
#api_v1.add_resource(UserLogin, '/login')
#api_v1.add_resource(UserLogout, '/logout')
#api_v1.add_resource(RefreshToken, '/refresh')
#api_v1.add_resource(UserInfo, '/me')

url = 'http://81.163.25.103:5000' # The root of the flask app
prefix = '/api/v1'
credentials = {
    "login": "test_user",
    "email": "test_email@mail.com",
    "password": "pass123"
}


@pytest.fixture(scope='session')
def token():
    r = requests.post(url+'/api/v1/login', params=credentials)
    data = r.json()
    return data

def test_me(token):
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    r = requests.get(url+'/api/v1/me', params=credentials, headers=headers)
    assert r.status_code == 200
    assert r.json()['login'] == 'test_user'

def test_admin(token):
    r = requests.get(url+'/api/v1/admin')
    assert r.status_code == 200

def test_create_admin_role():
    endpoint = '/role'
    params = {'name':'admin', 'description':'administrator'}
    r = requests.post(url+prefix+endpoint, params=params)
    assert r.status_code == 200

def test_asign_admin_role():
    params = {
        "login": "test_user",
        "name": "admin",
    }
    endpoint = '/assign_role'
    r = requests.post(url+prefix+endpoint, params=params)
    print(r.json())
    assert False

def test_get_role(token):
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    endpoint = '/role'
    r = requests.get(url+prefix+endpoint, headers=headers)
    print(r.json())
    assert False
