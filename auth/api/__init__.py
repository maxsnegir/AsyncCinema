from flask import Flask
from flask_restful import Api

from api.v1.users import UserRegister, UserLogin, UserInfo, RefreshToken, UserLogout

api_v1 = Api(prefix="/api/v1")
api_v1.add_resource(UserRegister, '/register')
api_v1.add_resource(UserLogin, '/login')
api_v1.add_resource(UserLogout, '/logout')
api_v1.add_resource(RefreshToken, '/refresh')
api_v1.add_resource(UserInfo, '/me')


def init_api(app: Flask):
    api_v1.init_app(app)
