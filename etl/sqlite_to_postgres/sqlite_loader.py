import sqlite3
from contextlib import contextmanager

from dataclasses_models import FilmWork, Genre, Person, FilmWorkGenre, PersonFilmWork


@contextmanager
def sqlite_connection(database_path: str):
    """ Контекстный менеджер для соединения с sqlite """

    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


class SQLiteLoader:
    """ Класс получения данных из базы SqlLite """

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def load_movies(self) -> dict:
        """ Возвращает словарь с данными из таблиц person, film_work, genre... """

        tables = {
            'film_work': FilmWork,
            'genre': Genre,
            'person': Person,
            'genre_film_work': FilmWorkGenre,
            'person_film_work': PersonFilmWork
        }
        data = {}
        for table, _dataclass in tables.items():
            query = f"""SELECT * FROM {table}"""
            res = [_dataclass(**row) for row in self.cursor.execute(query)]
            data[table] = res

        return data
