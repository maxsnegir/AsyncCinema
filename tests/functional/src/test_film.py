from http import HTTPStatus

import pytest
from elasticsearch._async.helpers import async_bulk

from functional.utils.data_generator import gen_film_data
from functional.utils.helper import gen_body_for_put_in_es, gen_body_for_del_from_es


class TestFilm:
    index = "movies"

    @pytest.mark.asyncio
    async def test_film_list_without_params(self, make_get_request, es_client):
        """Тест эндпоинта /film/"""

        films = gen_film_data(50)
        await async_bulk(es_client, gen_body_for_put_in_es(films, self.index))
        response = await make_get_request('/film')

        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        assert len(response.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response.body, list), "Неправильный тип данных в ответе"

        sorted_by_desc_response = sorted(response.body, key=lambda film: film["imdb_rating"], reverse=True)
        assert sorted_by_desc_response == response.body, "Фильмы не отсортированы по рейтингу"
        await async_bulk(es_client, gen_body_for_del_from_es(films, self.index))
