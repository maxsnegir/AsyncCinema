from http import HTTPStatus

from flask import jsonify, make_response
from flask_jwt_extended import current_user, jwt_required
from flask_jwt_extended import get_jwt
from flask_restful import Resource, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from db import db
from db.datastore import user_datastore
from db.db_models import User
from services.token import TokenService
from .parsers import register_parser, login_parser, change_password_parser, change_user_data_parser
from email_validator import validate_email, EmailNotValidError


class UserRegister(Resource):

    def post(self):
        args = register_parser.parse_args()
        password = args.get('password')
        args["password"] = generate_password_hash(password)
        email = args["email"]
        try:
            valid = validate_email(email)
            args["email"] = valid.email
        except EmailNotValidError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

        try:
            user = user_datastore.create_user(**args)
            db.session.commit()
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="User with current login or email already exists")

        return make_response(jsonify(login=user.login), HTTPStatus.CREATED)


class UserLogin(Resource):

    def post(self):
        args = login_parser.parse_args()
        login = args.get("login")
        password = args.get("password")
        user = User.get_user_by_login(login)
        if not user or not user.check_password(password):
            abort(HTTPStatus.UNAUTHORIZED, message="Wrong login or password")

        token_service = TokenService()
        access_token, refresh_token = token_service.get_jwt_tokens(str(user.id))
        return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK)


class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jwt = get_jwt()
        token_service = TokenService()

        token_service.revoke_token(jwt)
        return make_response(jsonify(msg="Access token revoked"), HTTPStatus.OK)


class RefreshToken(Resource):

    @jwt_required(refresh=True)
    def post(self):
        jwt = get_jwt()
        identity = jwt["sub"]

        token_service = TokenService()
        if not token_service.validate_refresh_token(jwt):
            abort(HTTPStatus.BAD_REQUEST, message="Wrong refresh token")

        token_service.revoke_token(jwt)
        access_token, refresh_token = token_service.get_jwt_tokens(identity)
        return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK)


class UserInfo(Resource):

    @jwt_required()
    def get(self):
        return jsonify(
            id=current_user.id,
            password=current_user.password,  # ToDo удалить
            login=current_user.login,
            email=current_user.email,
            roles=current_user.roles
        )


class UserChangePassword(Resource):
    """Смена пароля пользователя"""

    @jwt_required()
    def post(self):
        jwt = get_jwt()
        token_service = TokenService()

        args = change_password_parser.parse_args()
        current_password = args["current_password"]
        new_password = args["new_password"]

        if not current_user.check_password(current_password):
            abort(HTTPStatus.BAD_REQUEST, message="Invalid current password")

        if current_password == new_password:
            abort(HTTPStatus.BAD_REQUEST, message="Passwords must didn't match")

        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        token_service.revoke_token(jwt)
        return make_response(jsonify(message='Password successfully changed, please login again'), HTTPStatus.OK)


class UserDataChange(Resource):

    @jwt_required()
    def post(self):
        args = change_user_data_parser.parse_args()
        login = args["login"]
        email = args["email"]

        if not login and not email:
            abort(HTTPStatus.BAD_REQUEST, message='Enter login or email to change')

        if login:
            current_user.login = login
        if email:
            try:
                validate_email(email)
            except EmailNotValidError as e:
                abort(HTTPStatus.BAD_REQUEST, message=str(e))
            current_user.email = email

        try:
            db.session.commit()
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message='Login or email already exists')

        return make_response(jsonify(
            id=current_user.id,
            password=current_user.password,  # ToDo удалить
            login=current_user.login,
            email=current_user.email,
            roles=current_user.roles), HTTPStatus.OK)
