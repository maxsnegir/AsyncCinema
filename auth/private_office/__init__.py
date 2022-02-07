from flask import Flask
from flask_restful import Api

from private_office.v1.lk import (LKUserRegister,
                                  LKUserLogin,
                                  LKRefreshToken,
                                  LKUserLogout,
                                  LKUserAuths,
                                  LKChangeLogin,
                                  LKChangePassword)

private_office_v1 = Api(prefix="/lk/v1")
private_office_v1.add_resource(LKUserRegister, '/register')
private_office_v1.add_resource(LKUserLogin, '/login')
private_office_v1.add_resource(LKUserLogout, '/logout')
private_office_v1.add_resource(LKRefreshToken, '/refresh')
private_office_v1.add_resource(LKUserAuths, '/auth_history')
private_office_v1.add_resource(LKChangeLogin, '/change_login')
private_office_v1.add_resource(LKChangePassword, '/change_password')


def init_private_office(app: Flask):
    private_office_v1.init_app(app)
