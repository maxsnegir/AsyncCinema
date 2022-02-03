from flask import Flask
from flask_redis import FlaskRedis

redis = FlaskRedis()


def init_redis(app: Flask) -> None:
    app.config["REDIS_URL"] = "redis://localhost:6379/0"  # ToDo поправить
    redis.init_app(app)
