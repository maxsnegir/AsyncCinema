import os
import logging

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

load_dotenv()

TABLES_TO_LOAD = ['film', 'person', 'genre']

db_dsl = {
    'dbname': os.environ.get('POSTGRES_DB'),
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
}

es_dsl = [{
    'host': os.environ.get('ELASTIC_HOST'),
    'port': os.environ.get('ELASTIC_PORT')
}]
