from datetime import timedelta
from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from flask_jwt_extended import current_user, jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from db import db
from db.datastore import user_datastore
from db.db_models import User
from jwt_helper import jwt_redis_blocklist
from .parsers import register_parser, login_parser


class UserRegister(Resource):

    def post(self):
        args = register_parser.parse_args()
        password = args.get('password')
        args["password"] = generate_password_hash(password)
        try:
            user = user_datastore.create_user(**args)
            db.session.commit()
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="User already exists")

        return jsonify(login=user.login), HTTPStatus.CREATED


class UserLogin(Resource):

    def post(self):
        args = login_parser.parse_args()
        login = args.get("login")
        password = args.get("password")

        user = User.query.filter_by(login=login).one_or_none()
        if not user or not user.check_password(password):
            return jsonify(message="Wrong login or password"), HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        return jsonify(access_token=access_token, refresh_token=refresh_token)


class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        jwt_redis_blocklist.set(jti, "", ex=timedelta(hours=1))
        return jsonify(msg="Access token revoked")


class RefreshToken(Resource):

    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token)


class UserInfo(Resource):

    @jwt_required()
    def get(self):
        return jsonify(
            id=current_user.id,
            password=current_user.password,  # Для примера
            login=current_user.login,
        )
