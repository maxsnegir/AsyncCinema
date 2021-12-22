from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch_dsl import Search, Q
from models.film import Film, FilmShort

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Получаем фильм по id, сначала ищем в кеше, затем в elasticsearch"""
        film = await self._get_film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return
            await self._put_film_to_cache(film)

        return film

    async def get_film_list(self, **params) -> List[FilmShort]:
        """Получаем список фильмов"""

        body = self.get_body_query(**params)
        docs = await self.elastic.search(index='movies', body=body)
        return [FilmShort(**dict(doc['_source'])) for doc in docs['hits']['hits']]

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        """Получаем фильм по id из elasticsearch"""

        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return
        return Film(**doc['_source'])

    async def _get_film_from_cache(self, film_id: str) -> Optional[Film]:
        """Достаем фильм из redis"""
        data = await self.redis.get(film_id)
        if not data:
            return

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        """Помещаем фильм в redis"""

        film_id = film.uuid
        film_json = film.json()
        await self.redis.set(film_id, film_json, expire=FILM_CACHE_EXPIRE_IN_SECONDS)

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
            body_query = body_query.query('nested', path='genre', query=Q("match", genre__uuid=filter_genre))
        if query:
            body_query = body_query.query("multi_match", query=query, fields=['title', 'description'])
        return body_query.to_dict()


@lru_cache
def get_film_service(redis: Redis = Depends(get_redis),
                     elastic: AsyncElasticsearch = Depends(get_elastic)) -> FilmService:
    return FilmService(redis, elastic)
