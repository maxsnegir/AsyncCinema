from typing import List, Tuple

from psycopg2.extensions import connection as _connection, cursor as _cursor

import sql_queries
from helpers import backoff
from state import State


class Extractor:
    def __init__(self, connection: _connection, state: State):
        self.connection = connection
        self.cursor: _cursor = self.connection.cursor()
        self.state = state
        self.bulk_size = 100

    def get_updated_at(self, table_name: str) -> str:
        """Получаем updated_at по ключу"""
        updated_at = self.state.get_state(table_name)
        if not updated_at:
            return '-infinity'
        return updated_at

    def get_ids(self, rows) -> Tuple:
        if not rows:
            return tuple()
        return tuple(row[0] for row in rows)

    @backoff()
    def execute_query(self, query: str, *args) -> List:
        """ Выполнение sql запроса """

        self.cursor.execute(query, args)
        rows = self.cursor.fetchmany(self.bulk_size)
        return rows

    def get_updated_persons(self) -> List:
        """Получить последние обновленные персоны"""
        updated_at = self.get_updated_at('persons')
        query = sql_queries.updated_persons
        data = self.execute_query(query, updated_at)
        return data

    def get_updated_genres(self) -> List:
        """Получить последние обновленные жанры"""
        updated_at = self.get_updated_at('genres')
        query = sql_queries.updated_genres
        data = self.execute_query(query, updated_at)
        return data

    def get_updated_films(self) -> List:
        """Получить последние обновленные фильмы"""
        updated_at = self.get_updated_at('movies')
        query = sql_queries.updated_film_works
        data = self.execute_query(query, updated_at)
        return data

    def get_updated_film_by_film(self, fw_ids) -> List:
        """Получить полную информацию о фильме по обновленным фильмам"""
        if not fw_ids:
            return []
        data = self.get_film_data_by_id(fw_ids)
        return data

    def get_film_data_by_id(self, fw_ids) -> List:
        """Получить полную информацию о фильме по идентификаторам"""
        query = sql_queries.film_work_data_by_ids
        data = self.execute_query(query, fw_ids)
        return data

    def get_film_work_by_genre(self, genres_ids) -> List:
        """Получить полную информацию о фильме по обновленным жанрам"""
        if not genres_ids:
            return []

        query = sql_queries.film_work_id_by_genre
        fw_data = self.execute_query(query, genres_ids)
        fw_ids = self.get_ids(fw_data)
        data = self.get_film_data_by_id(fw_ids)
        return data

    def get_updated_film_by_person(self, persons_ids) -> List:
        """Получить полную информацию о фильме по обновленным персонам"""
        if not persons_ids:
            return []
        query = sql_queries.film_work_id_by_person
        fw_data = self.execute_query(query, persons_ids)
        fw_ids = self.get_ids(fw_data)
        data = self.get_film_data_by_id(fw_ids)
        return data

    def get_films(self, genres_ids, persons_ids, movie_ids) -> List:
        """Получить все обновленные фильмы по связанным таблицам"""
        movie_data = []
        movie_data.extend(self.get_updated_film_by_person(persons_ids))
        movie_data.extend(self.get_film_work_by_genre(genres_ids))
        movie_data.extend(self.get_updated_film_by_film(movie_ids))
        return movie_data

    def get_data(self) -> dict:
        """Получить полную информацию об обновленных фильмах, жанрах, персонах"""
        data = {}
        genres = self.get_updated_genres()
        persons = self.get_updated_persons()
        movies = self.get_updated_films()
        movies_data = self.get_films(self.get_ids(genres), self.get_ids(persons), self.get_ids(movies))

        if genres:
            data['genres'] = genres
        if persons:
            data['persons'] = persons
        if movies_data:
            data['movies'] = movies_data

        return data


