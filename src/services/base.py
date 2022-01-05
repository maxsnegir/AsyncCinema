from pickle import loads, dumps
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError as ES_NotFoundError
from elasticsearch_dsl import Search, Q

from models.base import BaseModel

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class BaseService:

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index):
        self.redis = redis
        self.elastic = elastic
        self.index = index
        self.search_fields = []
        self.model = BaseModel

    async def get_by_id(self, instance_id: str):
        """Получаем объект по id"""

        instance = await self._get_from_cache(instance_id)
        if not instance:
            instance = await self._get_from_elastic(instance_id)
            if not instance:
                return None
            await self._put_to_cache(instance.uuid, instance)
        return instance

    async def get_list(self, **params):
        """Получаем список объектов"""

        docs = await self._get_from_cache(params)
        if not docs:
            body = self.get_body_query(**params)
            docs = await self.elastic.search(index=self.index, body=body)
            if not docs:
                return []
            await self._put_to_cache(params, docs)
        return [self.model(**dict(doc['_source'])) for doc in docs['hits']['hits']]

    async def _get_from_elastic(self, instance_id: str) -> Optional[BaseModel]:
        try:
            doc = await self.elastic.get(self.index, instance_id)
            return self.model(**doc['_source'])
        except ES_NotFoundError:
            return

    async def _put_to_cache(self, key, value):
        key = self.index + ":" + str(key)
        await self.redis.set(key, dumps(value), expire=CACHE_EXPIRE_IN_SECONDS)

    async def _get_from_cache(self, key):
        data = await self.redis.get(self.index + ":" + str(key))
        if data:
            return loads(data)

    def get_body_query(self, **params) -> dict:
        """Формируем тело запроса в elastic"""

        _sort = params.get('sort')
        page_number = params.get('page_number')
        page_size = params.get('page_size')
        filter_genre = params.get('filter_genre')
        query = params.get('query')
        person_id = params.get('person_id')

        body_query = Search(using=self.elastic, index=self.index)
        start = (page_number - 1) * page_size
        if start >= 1000:
            start = 1000 - page_size
        body_query = body_query[start: start + page_size]

        if _sort:
            body_query = body_query.sort(_sort)
        if query:
            body_query = body_query.query("multi_match", query=query, fields=self.search_fields)
        if filter_genre:
            body_query = body_query.query('nested', path='genre', query=Q("match", genre__id=filter_genre))
        if person_id:
            body_query = body_query.query(Q('nested', path='actors', query=Q("match", actors__uuid=person_id)) |
                                          Q('nested', path='directors', query=Q("match", directors__uuid=person_id)) |
                                          Q('nested', path='writers', query=Q("match", writers__uuid=person_id)))
        return body_query.to_dict()
