from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch_dsl import Search, Q
from models.film import Film, FilmShort
from services.base import BaseService


class FilmService(BaseService):
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Получаем фильм по id, сначала ищем в кеше, затем в elasticsearch"""
        film = await self._get_from_cache(Film, film_id)
        if not film:
            film = await self._get_from_elastic('movies', Film, film_id)
            if not film:
                return
            await self._put_to_cache(film)

        return film

    async def get_film_list(self, **params) -> List[FilmShort]:
        """Получаем список фильмов"""

        body = self.get_body_query(**params)
        docs = await self.elastic.search(index='movies', body=body)
        return [FilmShort(**dict(doc['_source'])) for doc in docs['hits']['hits']]

    def get_body_query(self, **params) -> dict:
        """Формируем тело запроса в elastic"""

        sort = params.get('sort')
        page_number = params.get('page_number')
        page_size = params.get('page_size')
        filter_genre = params.get('filter_genre')
        query = params.get('query')

        body_query = Search(using=self.elastic, index='movies')
        start = (page_number - 1) * page_size
        body_query = body_query[start: start + page_size]

        if sort:
            body_query = body_query.sort(sort)
        if filter_genre:
            body_query = body_query.query('nested', path='genre', query=Q("match", genre__id=filter_genre))
        if query:
            body_query = body_query.query("multi_match", query=query, fields=['title', 'description'])
        return body_query.to_dict()


@lru_cache
def get_film_service(redis: Redis = Depends(get_redis),
                     elastic: AsyncElasticsearch = Depends(get_elastic)) -> FilmService:
    return FilmService(redis, elastic)
