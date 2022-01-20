import logging
import os
from time import sleep

from dotenv import load_dotenv
from redis import Redis, exceptions

load_dotenv()
logger = logging.getLogger()


def wait_for_redis(redis_client: Redis) -> None:
    """ Ждем пока redis станет доступным """

    logger.info("Waiting for Redis")
    while True:
        try:
            redis_client.ping()
        except exceptions.ConnectionError:
            sleep(2)
        else:
            break
    logger.info("Redis connected")


if __name__ == '__main__':
    redis_client = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ['REDIS_PORT'])
    wait_for_redis(redis_client)
