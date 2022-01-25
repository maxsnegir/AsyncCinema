from http import HTTPStatus

import pytest

from ..utils.constants import TestErrors as err
from ..utils.helper import get_redis_key_by_params

pytestmark = pytest.mark.asyncio  # Noqa


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

    async def test_film_list_without_params(self, create_test_data, redis_client, make_get_request, settings,
                                            query_movie_params):
        """Тест эндпоинта /film/"""

        response = await make_get_request('/film')
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 50, err.WRONG_LEN
        assert isinstance(response.body, list), err.WRONG_RESPONSE_BODY

        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), err.REDIS_404

        resp_with_default_params = await make_get_request('/film', params=query_movie_params)
        assert response.body == resp_with_default_params.body, \
            'Запрос без параметров должен соответствовать запросу с параметрами по умолчанию'

    async def test_film_desc_sort(self, create_test_data, make_get_request, redis_client, settings,
                                  query_movie_params):
        """Тест параметра ?sort """

        response = await make_get_request('/film')
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 50, err.WRONG_LEN
        assert isinstance(response.body, list), err.WRONG_RESPONSE_BODY

        assert await redis_client.get(get_redis_key_by_params(
            settings.MOVIE_INDEX, query_movie_params)), err.REDIS_404
        sorted_by_desc = sorted(response.body, key=lambda film: film["imdb_rating"], reverse=True)
        assert sorted_by_desc == response.body, "Фильмы не отсортированы уменьшению рейтинга"

    async def test_film_asc_sort(self, create_test_data, make_get_request, redis_client, settings, query_movie_params):
        """Тест параметра ?sort """

        query_movie_params["sort"] = "imdb_rating"
        response = await make_get_request('/film', params=query_movie_params)
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 50, err.WRONG_LEN
        assert isinstance(response.body, list), err.WRONG_RESPONSE_BODY
        sorted_by_asc = sorted(response.body, key=lambda film: film["imdb_rating"], reverse=False)
        assert response.body == sorted_by_asc, 'Фильмы должны возвращаться по возрастанию рейтинга'
        assert await redis_client.get(get_redis_key_by_params(
            settings.MOVIE_INDEX, query_movie_params)), err.REDIS_404

    async def test_film_page_number_param(self, create_test_data, make_get_request, query_movie_params, redis_client,
                                          settings):
        """Тест параметра ?page_number"""

        query_movie_params["page_number"] = 2
        response = await make_get_request('/film', params=query_movie_params)
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 50, err.WRONG_LEN
        assert isinstance(response.body, list), err.WRONG_RESPONSE_BODY
        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), err.REDIS_404

        query_movie_params["page_number"] = 1
        response_with_first_number = await make_get_request('/film', params=query_movie_params)
        assert response_with_first_number.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response_with_first_number.body) == 50, err.WRONG_LEN
        assert isinstance(response_with_first_number.body, list), err.WRONG_RESPONSE_BODY
        assert response.body != response_with_first_number.body, 'Значения 1-ой и 2-ой страницы не должны совпадать'

    async def test_film_page_with_large_number(self, create_test_data, make_get_request):
        """Тест параметра ?page_number по валидации значения"""
        response = await make_get_request('/film', params={"page_number": 1000000})
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY, err.WRONG_GTE_PAGE_SIZE

    async def test_film_page_with_zero_number(self, create_test_data, make_get_request):
        """Тест параметра ?page_number по валидации значения"""
        response = await make_get_request('/film', params={"page_number": 0})
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY, err.WRONG_LTE_PAGE_SIZE

    async def test_fim_page_size_param(self, create_test_data, make_get_request, query_movie_params, redis_client,
                                       settings):
        """Тест параметра ?page_size"""

        query_movie_params["page_size"] = 60
        response = await make_get_request('/film', params=query_movie_params)
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 60, err.WRONG_LEN
        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), err.REDIS_404

    async def test_fim_with_zero_page_size_param(self, create_test_data, make_get_request):
        """Тест параметра ?page_size по валидации значения"""
        response = await make_get_request('/film', params={"page_size": 0})
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY, err.WRONG_LTE_PAGE_SIZE

    async def test_fim_with_large_page_size_param(self, create_test_data, make_get_request):
        """Тест параметра ?page_size по валидации значения"""
        response = await make_get_request('/film', params={"page_size": 1000000})
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY, err.WRONG_GTE_PAGE_SIZE

    async def test_film_genre_filter_with_existing_genre(self, create_test_data, make_get_request, query_movie_params,
                                                         redis_client, settings):
        """Тест параметра ?filter_genre для существующего жанра"""

        query_movie_params["filter_genre"] = '949386de-246e-4b8c-9968-257309c2e52b'
        response = await make_get_request('/film', params=query_movie_params)
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 6, err.WRONG_LEN
        assert await redis_client.get(
            get_redis_key_by_params(settings.MOVIE_INDEX, query_movie_params)), err.REDIS_404

    async def test_film_genre_filter_with_nonexistent_genre(self, create_test_data, make_get_request,
                                                            query_movie_params):
        """Тест параметра ?filter_genre для несуществующего жанра"""

        query_movie_params["filter_genre"] = 'ec2cd0db-fdfd-4e12-87a5-ac3a93c0398f'
        response = await make_get_request('/film', params=query_movie_params)
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 0, err.WRONG_LEN

    async def test_film_by_exising_id(self, create_test_data, make_get_request, redis_client, settings):
        """Тест эндопинта film/{film_id} с существующим фильмом"""

        existing_film = 'e6ddc3ce-6945-4a9e-b0d1-31b2ae39ffd8'
        response = await make_get_request(f'/film/{existing_film}')
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert isinstance(response.body, dict), err.WRONG_RESPONSE_BODY
        assert response.body.get("uuid") is not None, 'У фильма отсутствует uuid'
        assert await redis_client.get(settings.MOVIE_INDEX + ":" + existing_film), err.REDIS_404

    async def test_film_by_nonexistent_id(self, create_test_data, make_get_request):
        """Тест эндопинта film/{film_id} с несуществующим фильмом"""

        nonexistent_film = 'ec2cd0db-fdfd-4e12-87a5-ac3a93c0398f'
        response = await make_get_request(f'/film/{nonexistent_film}')
        assert response.status == HTTPStatus.NOT_FOUND, err.WRONG_STATUS

    async def test_film_search(self, create_test_data, make_get_request, query_movie_params):
        """Тест поиска по фильмам"""

        query_movie_params["query"] = "Star Wars"
        response = await make_get_request(f'/film/search/', params=query_movie_params)

        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 1, err.WRONG_LEN
        assert isinstance(response.body, list), err.WRONG_RESPONSE_BODY
