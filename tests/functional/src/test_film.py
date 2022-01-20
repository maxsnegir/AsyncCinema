from http import HTTPStatus

import pytest

from ..utils.helper import get_redis_key_by_params


@pytest.fixture
def query_movie_params() -> dict:
    """Дефолтные GET параметры для фильмов"""

    return {
        "sort": "-imdb_rating",
        "page_size": 50,
        "page_number": 1,
        "filter_genre": ""
    }


class TestFilm:

    @pytest.mark.asyncio
    async def test_film_list_without_params(self, create_test_data, redis_client, make_get_request, settings,
                                            query_movie_params):
        """Тест эндпоинта /film/"""

        response = await make_get_request('/film')
        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        assert len(response.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response.body, list), "Неправильный тип данных в ответе"

        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), 'Отсутствуют данные в redis'

        resp_with_default_params = await make_get_request('/film', params=query_movie_params)
        assert response.body == resp_with_default_params.body, 'Запрос без параметров должен соответствовать ' \
                                                               'запросу с параметрами по умолчанию'

    @pytest.mark.asyncio
    async def test_film_sort_param(self, create_test_data, make_get_request, redis_client, settings,
                                   query_movie_params):
        """Тест параметра ?sort"""

        response_by_desc_sort = await make_get_request('/film')
        assert response_by_desc_sort.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response_by_desc_sort.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response_by_desc_sort.body, list), "Неправильный тип данных в ответе"

        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), 'Отсутствуют данные в redis'
        sorted_by_desc = sorted(response_by_desc_sort.body, key=lambda film: film["imdb_rating"], reverse=True)
        assert sorted_by_desc == response_by_desc_sort.body, "Фильмы не отсортированы уменьшению рейтинга"

        query_movie_params["sort"] = "imdb_rating"
        response_by_asc_sort = await make_get_request('/film', params=query_movie_params)
        assert response_by_asc_sort.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response_by_asc_sort.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response_by_asc_sort.body, list), "Неправильный тип данных в ответе"
        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), 'Отсутствуют данные в redis'

        sorted_by_asc = sorted(response_by_asc_sort.body, key=lambda film: film["imdb_rating"], reverse=False)
        assert response_by_asc_sort.body == sorted_by_asc, 'Фильмы должны возвращаться по возрастанию рейтинга'

    @pytest.mark.asyncio
    async def test_film_page_number_param(self, create_test_data, make_get_request, query_movie_params, redis_client,
                                          settings):
        """Тест параметра ?page_number"""

        query_movie_params["page_number"] = 2

        response = await make_get_request('/film', params=query_movie_params)
        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response.body, list), "Неправильный тип данных в ответе"
        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), 'Отсутствуют данные в redis'

        query_movie_params["page_number"] = 1
        response_with_first_number = await make_get_request('/film', params=query_movie_params)
        assert response_with_first_number.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response_with_first_number.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response_with_first_number.body, list), "Неправильный тип данных в ответе"
        assert response.body != response_with_first_number.body, 'Значения 1-ой и 2-ой страницы не должны совпадать'

        response_with_big_page_number = await make_get_request('/film', params={"page_number": 1000000})
        assert response_with_big_page_number.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для номера страницы со значением > 1000'

        response_with_zero_page = await make_get_request('/film', params={"page_number": 0})
        assert response_with_zero_page.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для номера страницы со значением == 0'

    @pytest.mark.asyncio
    async def test_fim_page_size_param(self, create_test_data, make_get_request, query_movie_params, redis_client,
                                       settings):
        """Тест параметра ?page_size"""

        query_movie_params["page_size"] = 60
        response = await make_get_request('/film', params=query_movie_params)
        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response.body) == 60, "Неправильное количество фильмов"
        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), 'Отсутствуют данные в redis'

        query_movie_params["page_size"] = 0
        response_with_zero_page_size = await make_get_request('/film', params=query_movie_params)
        assert response_with_zero_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для размера страницы == 0'

        query_movie_params["page_size"] = 1000000
        response_with_large_page_size = await make_get_request('/film', params=query_movie_params)
        assert response_with_large_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для размера страницы > 1000'

    @pytest.mark.asyncio
    async def test_film_filter_genre_param(self, create_test_data, make_get_request, query_movie_params, redis_client,
                                           settings):
        """Тест параметра ?filter_genre"""

        query_movie_params["filter_genre"] = '949386de-246e-4b8c-9968-257309c2e52b'
        response = await make_get_request('/film', params=query_movie_params)
        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response.body) == 6, 'Должно быть 6 :)'
        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), 'Отсутствуют данные в redis'

        query_movie_params["filter_genre"] = 'ec2cd0db-fdfd-4e12-87a5-ac3a93c0398f'
        response_with_nonexistent_genre = await make_get_request('/film', params=query_movie_params)
        assert response_with_nonexistent_genre.status == HTTPStatus.OK, "Неверный статус ответа"
        assert len(response_with_nonexistent_genre.body) == 0, "Неверное количество фильмов"

    @pytest.mark.asyncio
    async def test_film_by_id(self, create_test_data, make_get_request, redis_client, settings):
        """Тест эндопинта film/{film_id}"""

        existing_film = 'e6ddc3ce-6945-4a9e-b0d1-31b2ae39ffd8'
        response = await make_get_request(f'/film/{existing_film}')
        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert isinstance(response.body, dict), 'Возвращается неправильный формат фильма'
        assert response.body.get("uuid") is not None, 'У фильма отсутствует uuid'
        assert await redis_client.get(settings.MOVIE_INDEX + ":" + existing_film), 'Отсутствуют данные в redis'

        nonexistent_film = 'ec2cd0db-fdfd-4e12-87a5-ac3a93c0398f'
        response_for_nonexistent_film = await make_get_request(f'/film/{nonexistent_film}')
        assert response_for_nonexistent_film.status == HTTPStatus.NOT_FOUND, 'Неправильный статус ответа'

    @pytest.mark.asyncio
    async def test_film_search(self, create_test_data, make_get_request, query_movie_params):
        """Тест поиска по фильмам"""

        query_movie_params["query"] = "Star Wars"
        response = await make_get_request(f'/film/search/', params=query_movie_params)

        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        assert len(response.body) == 1, "Неправильное количество фильмов"
        assert isinstance(response.body, list), "Неправильный тип данных в ответе"
