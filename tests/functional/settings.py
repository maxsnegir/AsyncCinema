import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()


class Settings(BaseSettings):
    SERVICE_URL: str = f'{os.environ.get("WEB_HOST")}:{os.environ.get("WEB_PORT")}'
    API_URL = "/api/v1"
    INDEX_MAP_PATH: Path = Field("tests/functional/testdata/es_schemas/")
    TEST_DATA_PATH: Path = Field("tests/functional/testdata/")
    MOVIE_INDEX: str = "movies"
    GENRE_INDEX: str = "genres"
    PERSON_INDEX: str = "persons"

    INDEXES = (MOVIE_INDEX, GENRE_INDEX, PERSON_INDEX)
    ES_PORT: int = os.environ.get("ELASTIC_PORT", 9200)
    ES_HOST: str = os.environ.get("ELASTIC_HOST", "localhost")
    REDIS_PORT: int = os.environ.get("REDIS_PORT", 6379)
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
