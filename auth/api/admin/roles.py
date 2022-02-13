from http import HTTPStatus

from flask import make_response, jsonify
from flask_jwt_extended import jwt_required
from flask_restplus import abort, Resource
from sqlalchemy.exc import IntegrityError

from api.admin import admin_namespace as namespace
from api.permissions import admin_permission
from db import db, db_session
from db.datastore import user_datastore
from db.db_models import Role, User
from .parsers import role_parser, change_role_parser


@namespace.route("/roles")
class RolesView(Resource):
    method_decorators = [jwt_required(), admin_permission]

    def post(self):
        """Создание роли"""

        args = role_parser.parse_args()
        try:
            with db_session():
                role = user_datastore.create_role(**args)
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message="Role already exists")
        return make_response(jsonify(id=role.id, name=role.name, description=role.description), HTTPStatus.CREATED)

    def get(self):
        """Список всех ролей"""

        roles = [{"id": str(role.id), "name": role.name, "description": role.description} for role in
                 Role.get_all_roles()]
        return roles, HTTPStatus.OK


@namespace.route("/roles/<uuid:role_id>")
class RoleView(Resource):
    method_decorators = [jwt_required(), admin_permission]

    def patch(self, role_id):
        """Изменение роли"""
        role = Role.query.get_or_404(role_id)
        args = change_role_parser.parse_args()
        name = args.get("name")
        description = args.get("description")
        if not name and not description:
            abort(HTTPStatus.BAD_REQUEST, message="Enter name or description to change")

        try:
            with db_session():
                if name:
                    if role.name in Role.Meta.BASE_ROLES:
                        abort(HTTPStatus.BAD_REQUEST, message="You cant change base role names")
                    role.name = name
                if description:
                    role.description = description
        except IntegrityError:
            abort(HTTPStatus.BAD_REQUEST, message=f"Role with name {name} already exists")

        return make_response(jsonify(id=role.id, name=role.name, description=role.description), HTTPStatus.OK)

    def delete(self, role_id):
        """Удаление роли"""

        role = Role.query.get_or_404(role_id)
        if role.name in Role.Meta.BASE_ROLES:
            abort(HTTPStatus.BAD_REQUEST, message="You can't delete base roles")

        db.session.delete(role)
        db.session.commit()
        return make_response(jsonify(message="Role deleted"), HTTPStatus.NO_CONTENT)


@namespace.route('/<uuid:user_id>/assign-role/<uuid:role_id>')
class UserRolesView(Resource):
    method_decorators = [jwt_required(), admin_permission]

    def post(self, user_id, role_id):
        """Присвоение роли пользователю"""

        user = User.query.get_or_404(user_id)
        role = Role.query.get_or_404(role_id)

        if not user_datastore.add_role_to_user(user, role):
            abort(HTTPStatus.BAD_REQUEST, message="Role already assigned")

        db.session.commit()
        user_roles = [role.name for role in user.roles]
        return make_response(jsonify(id=user.id, roles=user_roles), HTTPStatus.CREATED)

    def delete(self, user_id, role_id):
        """Удаление роли у пользователя"""

        user = User.query.get_or_404(user_id)
        role = Role.query.get_or_404(role_id)

        if not user_datastore.remove_role_from_user(user, role):
            abort(HTTPStatus.BAD_REQUEST, message="User hasn't current role")

        db.session.commit()
        user_roles = [role.name for role in user.roles]
        return make_response(jsonify(id=user.id, roles=user_roles), HTTPStatus.OK)
