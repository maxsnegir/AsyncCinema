import logging
import os
from time import sleep

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()
logger = logging.getLogger()


def wait_for_es(es_client: Elasticsearch) -> None:
    """ Ждем пока es станет доступным """

    while not es_client.ping():
        logger.info("Waiting for Elasticsearch")
        sleep(2)
    logger.info("Elasticsearch connected")


if __name__ == '__main__':
    es_client = Elasticsearch([f'{os.environ.get("ELASTIC_HOST")}:{os.environ.get("ELASTIC_PORT")}'])
    wait_for_es(es_client)
