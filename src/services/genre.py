from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base import BaseService


class GenreService(BaseService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index):
        super().__init__(redis, elastic, index)
        self.model = Genre


@lru_cache()
def get_genre_service(redis: Redis = Depends(get_redis),
                      elastic: AsyncElasticsearch = Depends(get_elastic)) -> GenreService:
    return GenreService(redis, elastic, 'genres')
