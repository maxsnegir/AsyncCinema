import asyncio
import http
from dataclasses import dataclass

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from .settings import Settings
from .utils.helper import create_and_fill_indexes


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def es_client(settings):
    client = AsyncElasticsearch(hosts=settings.ES_HOST)
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
async def redis_client(settings):
    redis = await aioredis.create_redis_pool((settings.REDIS_HOST, settings.REDIS_PORT))
    await redis.flushall()
    yield redis
    redis.close()


@pytest.fixture
def make_get_request(session, settings):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = f"http://{settings.SERVICE_URL}{settings.API_URL}{method}"
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope='session')
async def create_test_data(es_client, settings) -> None:
    """ Cоздание индекса в es """

    await create_and_fill_indexes(es_client, settings)
    yield
    for index in settings.INDEXES:
        await es_client.indices.delete(index=index, ignore=[http.HTTPStatus.BAD_REQUEST, http.HTTPStatus.NOT_FOUND])
