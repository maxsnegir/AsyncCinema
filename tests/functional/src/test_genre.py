from http import HTTPStatus

import pytest

from ..utils.helper import get_redis_key_by_params


@pytest.fixture
def query_genre_params() -> dict:
    """Дефолтные GET параметры для жанров"""

    return {
        "page_size": 50,
        "page_number": 1,
    }


class TestGenre:
    @pytest.mark.asyncio
    async def test_genre_list_without_params(self,
                                             # create_test_data,
                                             redis_client,
                                             make_get_request,
                                             query_genre_params,
                                             settings):
        """Тест эндпоинта /genre"""
        current_schema = "/genre"

        response = await make_get_request(current_schema)

        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        assert len(response.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response.body, list), "Неправильный тип данных в ответе"

        assert await redis_client.get(
            get_redis_key_by_params(settings.GENRE_INDEX, query_genre_params)), 'Отсутствуют данные в redis'

        response_with_page = await make_get_request(current_schema, params=query_genre_params)
        assert response.body == response_with_page.body, (
            "Запрос без параметров должен соответствовать запросу"
            "с параметрами по умолчанию"
        )

    @pytest.mark.asyncio
    async def test_genre_page_number_param(self,
                                           # create_test_data,
                                           make_get_request,
                                           query_genre_params,
                                           redis_client,
                                           settings):
        """Тест параметра ?page_number"""
        current_schema = "/genre"

        query_genre_params["page_number"] = 2

        response = await make_get_request(current_schema, params=query_genre_params)

        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response.body, list), "Неправильный тип данных в ответе"
        assert await redis_client.get(
            get_redis_key_by_params(settings.GENRE_INDEX, query_genre_params)), 'Отсутствуют данные в redis'

        query_genre_params["page_number"] = 1
        response_with_first_number = await make_get_request(current_schema, params=query_genre_params)

        assert response_with_first_number.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response_with_first_number.body) == 50, "Неправильное количество жанров"
        assert isinstance(response_with_first_number.body, list), "Неправильный тип данных в ответе"
        assert response.body != response_with_first_number.body, 'Значения 1-ой и 2-ой страницы не должны совпадать'

        response_with_big_page_number = await make_get_request(current_schema, params={"page_number": 10 ** 6})
        assert response_with_big_page_number.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для номера страницы со значением > 1000'

        response_with_zero_page = await make_get_request(current_schema, params={"page_number": 0})
        assert response_with_zero_page.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для номера страницы со значением == 0'

    @pytest.mark.asyncio
    async def test_fim_page_size_param(self,
                                       # create_test_data,
                                       make_get_request,
                                       query_genre_params,
                                       redis_client,
                                       settings):
        """Тест параметра ?page_size"""

        current_schema = "/genre"

        query_genre_params["page_size"] = 60
        response = await make_get_request(current_schema, params=query_genre_params)
        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response.body) == 60, "Неправильное количество жфнров"
        assert await redis_client.get(
            get_redis_key_by_params(settings.GENRE_INDEX, query_genre_params)), 'Отсутствуют данные в redis'

        query_genre_params["page_size"] = 0
        response_with_zero_page_size = await make_get_request(current_schema, params=query_genre_params)
        assert response_with_zero_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для размера страницы == 0'

        query_genre_params["page_size"] = 10 ** 6
        response_with_large_page_size = await make_get_request(current_schema, params=query_genre_params)
        assert response_with_large_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для размера страницы > 1000'

    @pytest.mark.asyncio
    async def test_genre_by_id(self,
                              make_get_request,
                              redis_client,
                              settings):
        """Тест эндопинта genre/{genre_id}"""

        existing_genre = "a434d0c9-9cf7-47e6-bdd2-5683fa0eb480"
        current_schema = "/genre"

        response = await make_get_request(f'{current_schema}/{existing_genre}')
        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert isinstance(response.body, dict), 'Возвращается неправильный формат жанра'
        assert response.body.get("uuid") is not None, 'У жанра отсутствует uuid'
        assert await redis_client.get(settings.GENRE_INDEX + ":" + existing_genre), 'Отсутствуют данные в redis'

        nonexistent_film = "11111f68-643e-4ddd-8f57-84b62538081a"
        response_for_nonexistent_film = await make_get_request(f'/film/{nonexistent_film}')
        assert response_for_nonexistent_film.status == HTTPStatus.NOT_FOUND, 'Неправильный статус ответа'