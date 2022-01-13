import http
from dataclasses import dataclass

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from .settings import Settings
from .utils.helper import create_and_full_index


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts='127.0.0.1:9200')
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope='session')
async def redis_client():
    redis = await aioredis.create_redis_pool(('localhost', 6379))
    await redis.flushall()
    yield redis
    redis.close()


@pytest.fixture
def make_get_request(session, settings):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = settings.SERVICE_URL + settings.API_URL + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture
async def create_film_environment(es_client, settings) -> None:
    """ Cоздание индекса в es """

    index = 'movies'
    path = f"{settings.BASE_INDEX_PATH}{index}.json"
    await create_and_full_index(es_client, path, index)
    yield

    # После завершения теста индекс удаляется
    await es_client.indices.delete(index='movies', ignore=[http.HTTPStatus.BAD_REQUEST, http.HTTPStatus.NOT_FOUND])
