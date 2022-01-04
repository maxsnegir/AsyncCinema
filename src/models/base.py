import orjson
from pydantic import BaseModel as PydanticBaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseModel(PydanticBaseModel):
    uuid: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
