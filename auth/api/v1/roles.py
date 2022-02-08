from functools import wraps
from http import HTTPStatus

from db import db
from db.datastore import user_datastore
from db.db_models import User
from flask import jsonify
from flask_jwt_extended import current_user, jwt_required, verify_jwt_in_request
from flask_restful import Resource, abort
from sqlalchemy.exc import IntegrityError

from .parsers import assign_role_parser, role_parser


def role_required(required_role: str):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            role = required_role
            if role in current_user.roles:
                return fn(*args, **kwargs)
            else:
                return abort(HTTPStatus.FORBIDDEN, message="Admins only!")

        return decorator

    return wrapper


class TestOnlyAdmin(Resource):
    @role_required("admin")
    def get(self):
        return jsonify(secret="super_secret")


class UserRole(Resource):
    @role_required("admin")
    def post(self):
        args = role_parser.parse_args()
        try:
            user_datastore.create_role(**args)
            db.session.commit()
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="Role already exists")

        return HTTPStatus.CREATED

    @jwt_required()
    def get(self):
        return jsonify(roles=[str(role.name) for role in current_user.roles])


class AssignRole(Resource):
    @role_required("admin")
    def post(self):
        args = assign_role_parser.parse_args()
        login = args.get("login")
        user = User.get_user_by_login(login)
        if not user:
            return abort(HTTPStatus.NOT_FOUND, message="User not found")
        role = user_datastore.find_or_create_role(args.get("name"))
        if role.name in user.roles:
            return abort(HTTPStatus.BAD_REQUEST, message="Role already assigned")
        user_datastore.add_role_to_user(user, role)
        db.session.commit()
        return jsonify(message=f"role {role.name} assigned to user {login}")

    @role_required("admin")
    def delete(self):
        args = assign_role_parser.parse_args()
        login = args.get("login")
        user = User.get_user_by_login(login)
        if not user:
            return abort(HTTPStatus.NOT_FOUND, message="User not found")
        role = user_datastore.find_or_create_role(args.get("name"))
        if role.name not in user.roles:
            return abort(
                HTTPStatus.BAD_REQUEST,
                message=f"Role {role.name} is not assigned to user {login}",
            )
        user_datastore.remove_role_from_user(user, role)
        db.session.commit()
