from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base import BaseService


class GenreService(BaseService):
    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._get_from_cache(Genre, genre_id)
        if not genre:
            genre = await self._get_from_elastic('genres', Genre, genre_id)
            if not genre:
                return None
            await self._put_to_cache(genre)

        return genre

    async def get_list(self,
                       sort: str = None,
                       page_size: int = None,
                       page_number: int = None) -> List:
        body_query = Search(using=self.elastic, index='genres')
        start = (page_number - 1) * page_size
        body_query = body_query[start: start + page_size]
        if sort:
            body_query = body_query.sort(sort)
        body = body_query.to_dict()
        es_genres = await self.elastic.search(index='genres', body=body)
        genres = [Genre(**g['_source']) for g in es_genres['hits']['hits']]
        return genres


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
