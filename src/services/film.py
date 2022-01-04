from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, FilmShort
from services.base import BaseService


class FilmService(BaseService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index):
        super().__init__(redis, elastic, index)
        self.search_fields = ['title', 'description']
        self.model = Film

    async def get_list(self, **params):
        films = await super().get_list(**params)
        return [FilmShort(**dict(film)) for film in films]


@lru_cache
def get_film_service(redis: Redis = Depends(get_redis),
                     elastic: AsyncElasticsearch = Depends(get_elastic)) -> FilmService:
    return FilmService(redis, elastic, 'movies')
