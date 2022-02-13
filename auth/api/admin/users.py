from http import HTTPStatus

from email_validator import validate_email, EmailNotValidError
from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, current_user
from flask_restplus import Resource, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from api.admin import admin_namespace as namespace
from db import db, db_session
from db.datastore import user_datastore
from db.db_models import User, DefaultRoles, AuthHistory
from services.token import TokenService
from .parsers import register_parser, login_parser, change_password_parser


@namespace.route('/register')
class Register(Resource):

    def post(self):
        args = register_parser.parse_args()
        password = args.get("password")
        args["password"] = generate_password_hash(password)
        email = args["email"]
        try:
            valid = validate_email(email)
            args["email"] = valid.email
        except EmailNotValidError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

        try:
            with db_session():
                user = user_datastore.create_user(**args)
                user_datastore.add_role_to_user(user, DefaultRoles.USER)
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="User with current login or email already exists")

        return make_response(jsonify(login=user.login), HTTPStatus.CREATED)


@namespace.route('/login')
class Login(Resource):

    def post(self):
        args = login_parser.parse_args()
        login = args.get("login")
        password = args.get("password")
        user = User.get_user_by_login(login)
        if not user or not user.check_password(password):
            abort(HTTPStatus.UNAUTHORIZED, message="Wrong login or password")

        AuthHistory.create_history_record(user, request)
        token_service = TokenService(user)
        access_token, refresh_token = token_service.get_jwt_tokens()
        return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK)


@namespace.route('/logout')
class Logout(Resource):

    @jwt_required()
    def post(self):
        jwt = get_jwt()
        TokenService.revoke_token(jwt)
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

    @jwt_required()
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
