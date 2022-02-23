from datetime import timedelta

from pydantic import BaseSettings, Field, AnyUrl, validator


class DBSettings(BaseSettings):
    PROTOCOL: str = ""
    PORT: str = ""
    HOST: str = ""
    DATABASE: str = ""
    PASSWORD: str = ""
    USER: str = ""
    DSN: AnyUrl = None

    @validator("DSN", pre=True)
    def get_dsn(cls, value, values) -> str:
        if value:
            return value

        protocol = values["PROTOCOL"]
        user = values["USER"]
        password = values["PASSWORD"]
        host = values["HOST"]
        port = values["PORT"]
        database = values["DATABASE"]

        if user and password:
            return f"{protocol}://{user}:{password}@{host}:{port}/{database}"

        return f"{protocol}://{host}:{port}/{database}"

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'


class PostgresSettings(DBSettings):
    PROTOCOL: str = "postgresql"
    DATABASE: str = Field("auth_database", env="POSTGRES_DB")
    PASSWORD: str = Field("admin_passoword", env="POSTGRES_PASSWORD")
    USER: str = Field("admin", env="POSTGRES_USER")
    HOST: str = Field("localhost", env="DB_HOST")
    PORT: int = Field(5439, env="DB_PORT")


class RedisSettings(DBSettings):
    PROTOCOL: str = "redis"
    HOST: str = Field("localhost", env="REDIS_HOST")
    PORT: int = Field("6379", env="REDIS_PORT")
    DATABASE: str = "0"


class JWTSettings(BaseSettings):
    JWT_SECRET_KEY = Field("super-secret", env="JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'


class OAuthSettings(BaseSettings):
    YANDEX_CLIENT_ID = Field("1234", env="YANDEX_CLIENT_ID")
    YANDEX_CLIENT_SECRET = Field("1234", env="YANDEX_CLIENT_SECRET")
    YANDEX_ACCESS_TOKEN_URL = "https://oauth.yandex.ru/token"
    YANDEX_USERINFO_ENDPOINT = "https://login.yandex.ru/info"
    YANDEX_AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"

    MAIL_CLIENT_ID = Field("1234", env="MAIL_CLIENT_ID")
    MAIL_CLIENT_SECRET = Field("1234", env="MAIL_CLIENT_SECRET")
    MAIL_ACCESS_TOKEN_URL = "https://oauth.mail.ru/token"
    MAIL_USERINFO_ENDPOINT = "https://oauth.mail.ru/userinfo"
    MAIL_AUTHORIZE_URL = "https://oauth.mail.ru/login"

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'
