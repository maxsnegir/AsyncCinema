from uuid import uuid4

from flask_jwt_extended import create_access_token, create_refresh_token

from db.db_models import User
from storage import token_storage


class TokenService:

    def __init__(self, user: User):
        self.storage = token_storage
        self.user = user

    def get_jwt_tokens(self):
        identity = str(self.user.id)
        refresh_token_jti = str(uuid4())
        access_token = create_access_token(identity=identity,
                                           additional_claims={'is_admin': self.user.is_admin})
        refresh_token = create_refresh_token(identity=identity, additional_claims={"jti": refresh_token_jti})
        token_storage.set_refresh_token(identity, refresh_token_jti)
        return access_token, refresh_token

    @staticmethod
    def revoke_token(jwt):
        jti = jwt["jti"]
        identity = jwt["sub"]
        token_storage.set_revoked_refresh_token(jti)
        token_storage.delete_refresh_token(identity)

    @staticmethod
    def validate_access_token(jwt):
        identity = jwt["sub"]
        token = token_storage.get_token(identity)
        if not token:
            return False
        return True

    @staticmethod
    def validate_refresh_token(jwt):
        jti = jwt["jti"]
        identity = jwt["sub"]

        token = token_storage.get_token(identity)
        if not token or token != jti:
            return False
        return True
