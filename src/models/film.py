from typing import List, Union, Dict, Optional
from uuid import UUID

from pydantic import BaseModel

from models.base import OrjsonBaseModel


class Film(OrjsonBaseModel):
    uuid: str
    title: str
    description: Union[str, None]
    imdb_rating: float
    genre: Union[List[Dict[Union[str, UUID], str]], None]
    actors: Union[List[Dict[Union[str, UUID], str]], None]
    directors: Union[List[Dict[Union[str, UUID], str]], None]
    writers: Union[List[Dict[Union[str, UUID], str]], None]


class FilmShort(BaseModel):
    title: str
    description: Union[str, None]
    imdb_rating: Optional[float]
