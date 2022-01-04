from typing import Optional

from models.base import BaseModel


class Genre(BaseModel):
    name: str
    description: Optional[str]
