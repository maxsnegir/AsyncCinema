from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_restplus import abort


def admin_permission(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        verify_jwt_in_request()
        jwt = get_jwt()
        if jwt["is_admin"]:
            return fn(*args, **kwargs)
        else:
            abort(HTTPStatus.FORBIDDEN, message="Admins only!")

    return decorator
