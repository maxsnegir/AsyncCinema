import json
from typing import List, Generator

from elasticsearch._async.helpers import async_bulk  # Noqa

from .data_generator import generate_data


async def create_and_full_index(es_client, path, index):
    """Создаем индекс и заполняем тестовыми данными"""

    with open(path) as f:
        index_body = json.load(f)

    await es_client.indices.create(index=index, body=index_body, ignore=400)
    docs = generate_data(index)()
    await put_docs_to_es(es_client, docs, index)


async def put_docs_to_es(es_client, data, index):
    """Помещаем в индекс документы"""
    await async_bulk(es_client, gen_body_for_put_in_es(data, index))
    await wait_for_load(es_client, index)


def gen_body_for_put_in_es(docs: List[dict], index) -> Generator:
    """ Формируем формат для bulk запроса """

    for doc in docs:
        yield {
            "_index": index,
            "_id": doc.get("uuid"),
            **doc
        }


async def wait_for_load(es_client, index):
    """Ждем пока документы появятся elastic"""

    items_count = 0
    while not items_count:
        index_data = await es_client.count(index=index)
        items_count = index_data.get("count")
