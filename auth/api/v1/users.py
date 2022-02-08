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
from .parsers import register_parser, login_parser


class UserRegister(Resource):

    def post(self):
        args = register_parser.parse_args()
        password = args.get('password')
        args["password"] = generate_password_hash(password)
        try:
            user = user_datastore.create_user(**args)
            db.session.commit()
            return make_response(jsonify(login=user.login)), HTTPStatus.CREATED
        except IntegrityError:
            return abort(HTTPStatus.BAD_REQUEST, message="User already exists")
          

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
        jti = jwt["jti"]
        identity = jwt["sub"]
        token_service = TokenService()

        if not token_service.validate_access_token(identity):
            abort(HTTPStatus.UNAUTHORIZED, message="You are not login")
        token_service.revoke_token(jti, identity)
        return make_response(jsonify(msg="Access token revoked"), HTTPStatus.OK)


class RefreshToken(Resource):

    @jwt_required(refresh=True)
    def post(self):
        jwt = get_jwt()
        jti = jwt["jti"]
        identity = jwt["sub"]

        token_service = TokenService()
        if not token_service.validate_refresh_token(identity, jti):
            abort(HTTPStatus.BAD_REQUEST, message="Wrong refresh token")

        token_service.revoke_token(jti, identity)
        access_token, refresh_token = token_service.get_jwt_tokens(identity)
        return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK)


class UserInfo(Resource):

    @jwt_required()
    def get(self):
        return jsonify(
            id=current_user.id,
            password=current_user.password,  # Для примера
            login=current_user.login,
        )
