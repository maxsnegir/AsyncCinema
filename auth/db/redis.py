from flask import Flask
from flask_redis import FlaskRedis

from settings import RedisSettings

redis = FlaskRedis(strict=True)


def init_redis(app: Flask) -> None:
    app.config["REDIS_URL"] = RedisSettings().DSN
    redis.init_app(app)
