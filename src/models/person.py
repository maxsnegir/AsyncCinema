import datetime
from typing import Optional, List

from uuid import UUID

from models.base import OrjsonBaseModel


class Person(OrjsonBaseModel):
    id: UUID
    full_name: Optional[str]
    birth_date: Optional[datetime.date]
    role: Optional[List[str]]
    film_ids: Optional[List[str]]
