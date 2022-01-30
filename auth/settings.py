from pydantic import BaseSettings, Field, AnyUrl, validator


class PostgresSettings(BaseSettings):
    PROTOCOL: str = "postgresql"
    DATABASE: str = Field("postgres", env="POSTGRES_DB")
    PASSWORD: str = Field("postgres", env="POSTGRES_PASSWORD")
    POSTGRES_USER: str = Field("postgres", env="POSTGRES_USER")
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: int = Field(5432, env="DB_PORT")
    DSN: AnyUrl = None

    @validator("DSN", pre=True)
    def build_dsn(cls, value, values) -> str:
        if value:
            return value

        protocol = values["PROTOCOL"]
        user = values["POSTGRES_USER"]
        password = values["PASSWORD"]
        host = values["DB_HOST"]
        port = values["DB_PORT"]
        path = values["DATABASE"]

        if user and password:
            return f"{protocol}://{user}:{password}@{host}:{port}/{path}"

        return f"{protocol}://{host}:{port}/{path}"

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'
