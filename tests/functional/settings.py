from pydantic import BaseSettings


class Settings(BaseSettings):
    SERVICE_URL: str = 'http://localhost:8001'  # ToDO поправить перед деплоем
    API_URL = "/api/v1"
    BASE_INDEX_PATH = "../testdata/es_schemas/"
