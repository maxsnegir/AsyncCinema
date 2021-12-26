from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError as ES_NotFoundError
from pydantic import BaseModel


CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, id: str) -> Optional[BaseModel]:
        instance = await self._get_from_cache(id)
        if not instance:
            instance = await self._get_from_elastic(id)
            if not instance:
                return None
            await self._put_to_cache(instance)

        return instance

    async def _get_from_elastic(self, index: str, model: BaseModel, id: str) -> Optional[BaseModel]:
        try:
            doc = await self.elastic.get(index, id)
            return model(**doc['_source'])
        except ES_NotFoundError:
            return

    async def _get_from_cache(self, model: BaseModel, id: str) -> Optional[BaseModel]:
        data = await self.redis.get(id)
        if not data:
            return None

        instance = model.parse_raw(data)
        return instance

    async def _put_to_cache(self, instance: BaseModel):
        await self.redis.set(str(instance.id), instance.json(), expire=CACHE_EXPIRE_IN_SECONDS)
