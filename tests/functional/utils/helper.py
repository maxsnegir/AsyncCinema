import json
from typing import List, Generator

from elasticsearch._async.helpers import async_bulk  # Noqa


async def create_and_full_indexes(es_client, settings):
    """Создаем индекс и заполняем тестовыми данными"""

    for index in settings.INDEXES:
        index_map_path = settings.INDEX_MAP_PATH.joinpath(f"{index}.json")
        index_body = read_file(index_map_path)
        await es_client.indices.create(index=index, body=index_body, ignore=400)

        test_docs_path = settings.TEST_DATA_PATH.joinpath(f"{index}.json")
        test_docs = read_file(test_docs_path)
        await put_docs_to_es(es_client, test_docs, index)


def read_file(file_path: str):
    with open(file_path) as f:
        data = json.load(f)
    return data


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


def get_redis_key_by_params(index_name: str, params: dict) -> str:
    """ Формируем redis key в формате es_index:get_param1:get_param_2...get_param_n"""

    return index_name + ":" + ":".join([str(value) for value in params.values()])
