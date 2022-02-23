import os
from datetime import datetime
from http import HTTPStatus

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from db.redis import redis

load_dotenv()

REQUEST_LIMIT_PER_MINUTE = int(os.environ.get('RPS_COUNT', 20))


def init_middleware(app: Flask):
    @app.before_request
    def rps_limit():
        pipline = redis.pipeline()
        key = f"{request.remote_addr}:{datetime.now().minute}"
        pipline.incr(key, 1)
        pipline.expire(key, 59)
        res = pipline.execute()
        if res[0] > REQUEST_LIMIT_PER_MINUTE:
            return jsonify(message="Too many requests"), HTTPStatus.TOO_MANY_REQUESTS
