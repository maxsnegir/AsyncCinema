from flask import Flask
from flask_restful import Api

from private_office.v1.lk import (
                                  LKUserAuths,
                                  LKChangeLogin,
                                  LKChangePassword)

private_office_v1 = Api(prefix="/lk/v1")
private_office_v1.add_resource(LKChangeLogin, '/change_login')
private_office_v1.add_resource(LKChangePassword, '/change_password')
private_office_v1.add_resource(LKUserAuths, '/auth_history')


def init_private_office(app: Flask):
    private_office_v1.init_app(app)
