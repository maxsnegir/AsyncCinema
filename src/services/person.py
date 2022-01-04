from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.base import BaseService


class PersonService(BaseService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index):
        super().__init__(redis, elastic, index)
        self.model = Person
        self.fields = ['full_name']


@lru_cache()
def get_person_service(redis: Redis = Depends(get_redis),
                       elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonService:
    return PersonService(redis, elastic, 'persons')
