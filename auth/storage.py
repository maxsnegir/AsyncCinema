from redis import Redis

from db.redis import redis


class TokenStorage:
    def __init__(self, storage: Redis):
        self.storage = storage

    def set_refresh_token(self, user_id: str, refresh_token: str) -> None:
        self.storage.set(user_id, refresh_token)

    def set_revoked_refresh_token(self, refresh_token: str) -> None:
        self.storage.set(refresh_token, "", 15)

    def delete_refresh_token(self, user_id: str) -> None:
        self.storage.delete(user_id)

    def get_token(self, user_id: str) -> str:
        token = self.storage.get(user_id)
        if token:
            return token.decode()
        return ""


token_storage = TokenStorage(redis)
