import logging
import os
import sqlite3

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from sqlite_loader import SQLiteLoader, sqlite_connection
from postgres_saver import PostgresSaver

load_dotenv()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    try:
        postgres_saver = PostgresSaver(pg_conn)
        sqlite_loader = SQLiteLoader(connection)
        data = sqlite_loader.load_movies()
        postgres_saver.save_all_data(data)
    except sqlite3.OperationalError:
        logging.exception('Ошибка при выгрузке данных из sqlite')
    except psycopg2.Error:
        logging.exception('Ошибка при загрузке данных в psql')
    except Exception:
        logging.exception('Непредвиденная ошибка')


if __name__ == '__main__':

    dsl = {'dbname': os.environ.get('POSTGRES_DB'),
           'user': os.environ.get('POSTGRES_USER'),
           'password': os.environ.get('POSTGRES_PASSWORD'),
           'host': os.environ.get('DB_HOST'),
           'port': os.environ.get('DB_PORT'),
           }

    with sqlite_connection("db.sqlite") as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
