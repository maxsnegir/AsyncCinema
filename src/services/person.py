from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search, Q
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.base import BaseService


class PersonService(BaseService):
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._get_from_cache(Person, person_id)
        if not person:
            person = await self._get_from_elastic('persons', Person, person_id)
            if not person:
                return None
            await self._put_to_cache(person)

        return person

    async def get_list(self,
                       sort: str = None,
                       page_size: int = None,
                       page_number: int = None,
                       filter_role: str = None) -> List:
        body_query = Search(using=self.elastic, index='persons')
        start = (page_number - 1) * page_size
        body_query = body_query[start: start + page_size]

        if filter_role:
            for role in filter_role:
                body_query = body_query.query("match", role=role)
        if sort:
            body_query = body_query.sort(sort)
        body = body_query.to_dict()
        es_persons = await self.elastic.search(index='persons', body=body)
        persons = [Person(**g['_source']) for g in es_persons['hits']['hits']]
        return persons


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
