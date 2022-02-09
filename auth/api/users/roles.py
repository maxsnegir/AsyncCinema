from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restplus import Resource

from api.permissions import admin_permission
from api.admin import admin_namespace as namespaces
from db.db_models import User, Role


@namespaces.route("/<uuid:user_id>/has-role/<uuid:role_id>")
class UserRoleCheck(Resource):
    method_decorators = [jwt_required(), admin_permission]

    def get(self, user_id, role_id):
        user = User.query.get_or_404(user_id)
        role = Role.query.get_or_404(role_id)

        return jsonify(user_id=user.id, role_name=role.name, has_role=user.has_role(role))
