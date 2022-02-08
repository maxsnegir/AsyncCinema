from functools import wraps
from http import HTTPStatus

from db import db
from db.datastore import user_datastore
from db.db_models import User, Role
from flask import jsonify, make_response
from flask_jwt_extended import current_user, verify_jwt_in_request
from flask_restful import Resource, abort
from sqlalchemy.exc import IntegrityError

from .parsers import assign_role_parser, create_role_parser, get_role_parser, patch_role_parser


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


class UserRole(Resource):
    @role_required("admin")
    def post(self):
        args = create_role_parser.parse_args()
        try:
            user_datastore.create_role(**args)
            db.session.commit()
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="Role already exists")

        return HTTPStatus.CREATED


    @role_required("admin")
    def get(self):
        args = get_role_parser.parse_args()
        name = args.get('name')
        if name:
            role = Role.get_role_by_name(name)
            return jsonify(name=role.name, description=role.description)
        else:
            return jsonify({role.name:role.description for role in Role.get_all()})

    @role_required("admin")
    def patch(self):
        args = patch_role_parser.parse_args()
        _id = args.get('id')
        _name = args.get('name')
        description = args.get('description')
        if _id:
            role = Role.get_role_by_id(_id)
            role.name = _name
            role.description = description
            db.session.commit()
            return make_response(jsonify({"message":"role updated"}), 200)

        if _name:
            role = Role.get_role_by_name(_name)
            role.description = description
            db.session.commit()
            return make_response(jsonify({"message":"role updated"}), 200)


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
