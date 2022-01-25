import logging
import os
from time import sleep, time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

WAIT_TIME = 60

load_dotenv()
logger = logging.getLogger()


def wait_for_es(es_client: Elasticsearch) -> None:
    """ Ждем пока es станет доступным """

    logger.info("Waiting for Elasticsearch")
    waiting_start = time()
    while not es_client.ping():
        sleep(2)
        if time() - waiting_start > WAIT_TIME:
            logger.error("Elasticsearch connection timeout")
            raise ConnectionError
    logger.info("Elasticsearch connected")


if __name__ == '__main__':
    es_client = Elasticsearch([f'{os.environ.get("ELASTIC_HOST")}:{os.environ.get("ELASTIC_PORT")}'])
    wait_for_es(es_client)
