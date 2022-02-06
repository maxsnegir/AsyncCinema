from http import HTTPStatus
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource, abort
from flask_security import roles_required
from sqlalchemy.exc import IntegrityError
from flask import jsonify
from db.datastore import user_datastore
from .parsers import role_parser
from db import db
from db.db_models import User

class TestOnlyAdmin(Resource):

    @roles_required('admin')
    def get(self):
        return jsonify(secret='super_secret')


class UserRole(Resource):
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
        return current_user.roles

class AssignRole(Resource):
    def post(self):
        args = role_parser.parse_args()
        login = args.get('login')
        user = User.get_user_by_login(login)
        if not user:
            abort(HTTPStatus.NOT_FOUND, message="User not found")
        #user = user_datastore.get_user(identifier) # Returns a user matching the specified ID or email addres
        role = user_datastore.find_or_create_role(args.get('name'))
        try:
            user_datastore.add_role_to_user(user, role)
            db.session.commit()
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="Role already assigned")
