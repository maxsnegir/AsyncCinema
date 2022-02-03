from uuid import uuid4

from flask_jwt_extended import create_access_token, create_refresh_token

from storage import token_storage


class TokenService:

    def __init__(self):
        self.storage = token_storage

    @staticmethod
    def get_jwt_tokens(user_id):
        identity = str(user_id)
        refresh_token_jti = str(uuid4())
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity, additional_claims={"jti": refresh_token_jti})
        token_storage.set_refresh_token(identity, refresh_token_jti)
        return access_token, refresh_token

    @staticmethod
    def revoke_token(token, user_id):
        token_storage.set_revoked_refresh_token(token)
        token_storage.delete_refresh_token(user_id)

    @staticmethod
    def validate_access_token(user_id):
        token = token_storage.get_token(user_id)
        if not token:
            return False
        return True

    @staticmethod
    def validate_refresh_token(user_id, token_jti):
        token = token_storage.get_token(user_id)
        if not token or token != token_jti:
            return False
        return True
