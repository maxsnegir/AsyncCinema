from typing import List, Union, Dict, Optional
from uuid import UUID
import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
    uuid: str
    title: str
    description: Union[str, None]
    imdb_rating: float
    genre: Union[List[Dict[Union[str, UUID], str]], None]
    actors: Union[List[Dict[Union[str, UUID], str]], None]
    directors: Union[List[Dict[Union[str, UUID], str]], None]
    writers: Union[List[Dict[Union[str, UUID], str]], None]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FilmShort(BaseModel):
    title: str
    description: Union[str, None]
    imdb_rating: Optional[float]
