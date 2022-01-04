import datetime
from typing import Optional, List

from models.base import BaseModel


class Person(BaseModel):
    full_name: Optional[str]
    birth_date: Optional[datetime.date]
    role: Optional[List[str]]
    film_ids: Optional[List[str]]
