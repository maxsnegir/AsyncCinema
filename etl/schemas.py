from pydantic import BaseModel
from typing import Union, List, Dict, Optional
from uuid import UUID


class FilmWork(BaseModel):
    id: Union[str, UUID]
    title: Union[str, None]
    description: Union[str, None]
    imdb_rating: Union[float, None]
    genre: Union[List[Dict[Union[str, UUID], str]], None]

    actors: Union[List[Dict[Union[str, UUID], str]], None]
    directors: Union[List[Dict[Union[str, UUID], str]], None]
    writers: Union[List[Dict[Union[str, UUID], str]], None]


class Genre(BaseModel):
    id: Union[str, UUID]
    name: Union[str, None]
    description: Union[str, None]


class Person(BaseModel):
    id: Union[str, UUID]
    full_name: Union[str, None]
    role: Union[List[str], None]
    film_ids: Union[List, None]
