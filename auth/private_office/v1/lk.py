import uuid
from http import HTTPStatus

from flask import jsonify, make_response, request
from flask_jwt_extended import current_user, jwt_required
from flask_jwt_extended import get_jwt
from flask_restful import Resource, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from db import db
from sqlalchemy import select, update
from db.datastore import user_datastore
from db.db_models import User, UserAuthorizations
from services.token import TokenService
from . import register_parser, login_parser, change_login_parser, change_password_parser

from ip2geotools.databases.noncommercial import DbIpCity


class LKUserRegister(Resource):

    def post(self):
        args = register_parser.parse_args()
        password = args.get('password')
        args["password"] = generate_password_hash(password)
        try:
            user = user_datastore.create_user(**args)
            db.session.commit()
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="User already exists")

        return make_response(jsonify(login=user.login), HTTPStatus.CREATED)


class LKUserLogin(Resource):

    def post(self):
        args = login_parser.parse_args()
        login = args.get("login")
        password = args.get("password")
        user = User.get_user_by_login(login)
        if not user or not user.check_password(password):
            abort(HTTPStatus.UNAUTHORIZED, message="Wrong login or password")

        token_service = TokenService()
        access_token, refresh_token = token_service.get_jwt_tokens(str(user.id))

        # Добавляем информацию об авторизации
        user_agent = request.headers.get('User-Agent')
        user_ip = request.remote_addr
        user_geo = DbIpCity.get(user_ip, api_key='free').city

        user_info = UserAuthorizations(id=uuid.uuid4(),
                                       user_id=user.id,
                                       user_agent=user_agent,
                                       user_ip=user_ip,
                                       user_geo=user_geo
                                       )

        db.session.add(user_info)
        db.session.commit()

        return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK)


class LKUserLogout(Resource):

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


class LKRefreshToken(Resource):

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


class LKUserAuths(Resource):
    number_authentications = 5

    @jwt_required()
    def get(self):
        info_of_auth = select([UserAuthorizations])\
            .where(UserAuthorizations.user_id == current_user.id)

        engine = db.engine.engine

        connection = engine.connect()
        result = connection.execute(info_of_auth)

        raws = result.fetchmany(self.number_authentications)
        auths = {str(raw[0]): {'user-agent': raw[4], 'ip': raw[5], 'city': raw[6]} for raw in raws[::-1]}
        print(auths)
        return auths


class LKChangeLogin(Resource):
    @jwt_required()
    def put(self):
        args = change_login_parser.parse_args()
        new_login = args.get('new_login')

        if new_login and isinstance(new_login, str):

            query = update(User).where(User.id == current_user.id).values(login=new_login)

            engine = db.engine.engine

            connection = engine.connect()
            connection.execute(query)

            return jsonify(status='You are changes login!')
        return jsonify(status=f'Bad login: {new_login}')


class LKChangePassword(Resource):
    @jwt_required()
    def put(self):
        args = change_password_parser.parse_args()
        new_password = args.get('new_password')
        if new_password and isinstance(new_password, str):
            new_password = generate_password_hash(new_password)
            query = update(User).where(User.id == current_user.id)\
                .values(password=new_password)

            engine = db.engine.engine

            connection = engine.connect()
            connection.execute(query)
            return jsonify(status='You are changes password!')
        return jsonify(status=f'Bad password!')


class LKUserInfo(Resource):
    @jwt_required()
    def get(self):
        return jsonify(
            id=current_user.id,
            password=current_user.password,  # Для примера
            login=current_user.login,
        )
