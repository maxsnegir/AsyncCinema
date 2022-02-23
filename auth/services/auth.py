from http import HTTPStatus

from flask import request
from flask_restplus import abort

from db.db_models import AuthHistory
from services.token import TokenService
from .user import UserService


class AuthService:

    @classmethod
    def login(cls, login: str, password: str):
        user = UserService.get_user_by_login(login)
        if not user or not user.check_password(password):
            abort(HTTPStatus.UNAUTHORIZED, message="Wrong login or password")

        AuthHistory.create_history_record(user, request)
        token_service = TokenService(user)
        access_token, refresh_token = token_service.get_jwt_tokens()
        return access_token, refresh_token

    @classmethod
    def logout(cls, jwt):
        TokenService.revoke_token(jwt)
