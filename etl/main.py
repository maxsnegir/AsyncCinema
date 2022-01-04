import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

import config as conf
from elastic import ElasticsearchLoader
from extractor import Extractor
from schemas import FilmWork, Genre, Person
from state import State, JsonFileStorage


def etl(pg_connection: _connection) -> None:
    """Загрузка данных из базы в ElasticSearch"""

    state = State(JsonFileStorage("PostgresStorages.json"))
    es_movie = ElasticsearchLoader(conf.es_dsl, 'movies', 'es_schemas/movies.json')
    es_genre = ElasticsearchLoader(conf.es_dsl, 'genres', 'es_schemas/genres.json')
    es_person = ElasticsearchLoader(conf.es_dsl, 'persons', 'es_schemas/persons.json')
    extractor = Extractor(pg_connection, state)

    while True:
        data = extractor.get_data()
        if not data:
            break

        for key, value in data.items():
            if not value:
                continue

            if key == 'genres':
                es_genre.load_es_data([Genre(**dict(row)) for row in value])
                state.set_state(key, str(dict(value[-1]).get("updated_at")))

            elif key == 'persons':
                es_person.load_es_data([Person(**dict(row)) for row in value])
                state.set_state(key, str(dict(value[-1]).get("updated_at")))

            elif key == 'movies':
                es_movie.load_es_data([FilmWork(**dict(row)) for row in value])
                state.set_state(key, str(dict(value[-1]).get("updated_at")))


if __name__ == '__main__':
    try:
        with psycopg2.connect(**conf.db_dsl, cursor_factory=DictCursor) as pg_conn:
            etl(pg_conn)
    finally:
        pg_conn.close()
