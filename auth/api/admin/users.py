from http import HTTPStatus

from email_validator import EmailNotValidError
from flask import make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt, current_user
from flask_restplus import Resource, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from api.admin import admin_namespace as namespace
from db import db
from db.db_models import DefaultRoles
from services.auth import AuthService
from services.token import TokenService
from services.user import UserService
from utlis.validators import email_validator
from .parsers import register_parser, login_parser, change_password_parser


@namespace.route('/register')
class Register(Resource):

    @namespace.expect(register_parser)
    def post(self):
        args = register_parser.parse_args()
        password = args.get("password")
        login = args["login"]
        try:
            email = email_validator(args["email"])
        except EmailNotValidError as e:
            return abort(HTTPStatus.BAD_REQUEST, message=str(e))

        try:
            user = UserService.create_user(login, email, password, DefaultRoles.USER)
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="User with current login or email already exists")

        return make_response(jsonify(login=user.login, email=user.email), HTTPStatus.CREATED)


@namespace.route('/login')
class Login(Resource):

    @namespace.expect(login_parser)
    def post(self):
        args = login_parser.parse_args()
        login = args.get("login")
        password = args.get("password")
        access_token, refresh_token = AuthService.login(login, password)
        return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK)


@namespace.route('/logout')
class Logout(Resource):

    @jwt_required()
    def post(self):
        jwt = get_jwt()
        AuthService.logout(jwt)
        return make_response(jsonify(message="Access token revoked"), HTTPStatus.OK)


@namespace.route('/refresh')
class RefreshToken(Resource):

    @jwt_required(refresh=True)
    def post(self):
        jwt = get_jwt()
        token_service = TokenService(current_user)
        if not token_service.validate_refresh_token(jwt):
            abort(HTTPStatus.BAD_REQUEST, message="Wrong refresh token")

        token_service.revoke_token(jwt)
        access_token, refresh_token = token_service.get_jwt_tokens()
        return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK)


@namespace.route('/password-change')
class UserChangePassword(Resource):
    """Смена пароля пользователя"""
    method_decorators = [jwt_required(), ]

    @namespace.expect(change_password_parser)
    def post(self):

        args = change_password_parser.parse_args()
        current_password = args["current_password"]
        new_password = args["new_password"]

        if not current_user.check_password(current_password):
            abort(HTTPStatus.BAD_REQUEST, message="Invalid current password")

        if current_password == new_password:
            abort(HTTPStatus.BAD_REQUEST, message="Passwords must didn't match")

        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        jwt = get_jwt()
        TokenService.revoke_token(jwt)
        return make_response(jsonify(message='Password successfully changed, please login again'), HTTPStatus.OK)
