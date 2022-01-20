from pathlib import Path

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    SERVICE_URL: str = Field('http://localhost:8001')  # ToDO поправить перед деплоем
    API_URL = "/api/v1"
    INDEX_MAP_PATH: Path = Field("tests/functional/testdata/es_schemas/")
    TEST_DATA_PATH: Path = Field("tests/functional/testdata/")
    MOVIE_INDEX: str = "movies"
    GENRE_INDEX: str = "genres"
    PERSON_INDEX: str = "persons"

    INDEXES = (MOVIE_INDEX, GENRE_INDEX, PERSON_INDEX)
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
