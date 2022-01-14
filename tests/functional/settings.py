from pydantic import BaseSettings


class Settings(BaseSettings):
    SERVICE_URL: str = 'http://localhost:8001'  # ToDO поправить перед деплоем
    API_URL = "/api/v1"
    INDEX_MAP_PATH = "../testdata/es_schemas/"
    TEST_DATA_PATH = "../testdata/"
    INDEXES = ("movies", "genres", "persons")
