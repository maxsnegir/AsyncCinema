from http import HTTPStatus

from email_validator import validate_email, EmailNotValidError
from flask import jsonify, make_response
from flask_jwt_extended import jwt_required, current_user, get_jwt
from flask_restplus import Resource, abort
from sqlalchemy.exc import IntegrityError

from api.users import user_namespace as namespace
from api.users.parsers import change_user_data_parser
from db import db


@namespace.route('/me')
class UserInfo(Resource):

    @jwt_required()
    def get(self):
        return jsonify(
            id=current_user.id,
            login=current_user.login,
            email=current_user.email,
            roles=[role.name for role in current_user.roles]
        )


@namespace.route('/me/change')
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

        return make_response(jsonify(id=current_user.id, login=current_user.login, email=current_user.email,
                                     roles=[role.name for role in current_user.roles]), HTTPStatus.OK)
