from typing import List, Union, Dict, Optional
from uuid import UUID

from models.base import BaseModel


class Film(BaseModel):
    title: str
    description: Union[str, None]
    imdb_rating: Optional[float]
    genre: Union[List[Dict[Union[str, UUID], str]], None]
    actors: Union[List[Dict[Union[str, UUID], str]], None]
    directors: Union[List[Dict[Union[str, UUID], str]], None]
    writers: Union[List[Dict[Union[str, UUID], str]], None]


class FilmShort(BaseModel):
    title: str
    imdb_rating: Optional[float]
