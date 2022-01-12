from typing import List, Generator


def gen_body_for_put_in_es(docs: List[dict], index) -> Generator:
    """ Формируем формат для bulk запроса """

    for doc in docs:
        yield {
            "_index": index,
            "_id": doc.get("uuid"),
            **doc
        }


def gen_body_for_del_from_es(docs: List[dict], index):
    for doc in docs:
        yield {
            '_op_type': 'delete',
            '_index': index,
            '_id': doc.get("uuid"),
        }
