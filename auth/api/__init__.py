from flask import Flask
from flask_restful import Api

from api.v1.users import UserRegister, UserLogin, UserInfo, RefreshToken, UserLogout
from api.v1.roles import UserRole, AssignRole
from api.v1.users import UserRegister, UserLogin, UserInfo, RefreshToken, UserLogout, UserChangePassword, \
    UserDataChange

api_v1 = Api(prefix="/api/v1")
api_v1.add_resource(UserRegister, "/register")
api_v1.add_resource(UserLogin, "/login")
api_v1.add_resource(UserLogout, "/logout")
api_v1.add_resource(RefreshToken, "/refresh")
api_v1.add_resource(UserInfo, "/me")
api_v1.add_resource(UserRole, "/role", "/role/<role_id>")
api_v1.add_resource(AssignRole, "/assign_role")
api_v1.add_resource(UserDataChange, '/me/change')
api_v1.add_resource(UserChangePassword, '/password-change')


def init_api(app: Flask):
    api_v1.init_app(app)
