import json
from typing import List, Generator

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from config import logger
from helpers import backoff
from schemas import FilmWork


class ElasticsearchLoader:
    """Класс для загрузки данных в es """

    def __init__(self, conf: List, index_name: str, index_file_path: str):
        self.es = Elasticsearch(conf)
        self.index_file_path = index_file_path
        self.index_name = index_name
        self.create_index()

    def create_index(self) -> None:
        """ Cоздание индекса в es """

        if not self.es.indices.exists(index=self.index_name):
            with open(self.index_file_path) as f:
                index_body = json.load(f)
            self.es.indices.create(index=self.index_name, body=index_body)

    @backoff()
    def load_es_data(self, docs: List) -> None:
        """ Загружаем данные в es пачками """

        bulk(self.es, self.gen_data(docs), index=self.index_name)
        logger.info(f"Загружено {len(docs)} документов в es")

    def gen_data(self, docs: List[FilmWork]) -> Generator:
        """ Формируем формат для bulk запроса """

        for doc in docs:
            yield {
                "_index": self.index_name,
                "_id": doc.uuid,
                **doc.dict()
            }
