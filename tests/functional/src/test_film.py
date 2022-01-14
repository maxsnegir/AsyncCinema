from http import HTTPStatus

import pytest


class TestFilm:

    @pytest.mark.asyncio
    async def test_film_list_without_params(self, create_test_data, make_get_request):
        """Тест эндпоинта /film/"""

        response = await make_get_request('/film')

        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        assert len(response.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response.body, list), "Неправильный тип данных в ответе"

        sorted_by_desc_response = sorted(response.body, key=lambda film: film["imdb_rating"], reverse=True)
        assert sorted_by_desc_response == response.body, "Фильмы не отсортированы по рейтингу"
