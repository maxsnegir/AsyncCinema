from http import HTTPStatus

import pytest

from ..utils.constants import TestErrors as err
from ..utils.helper import get_redis_key_by_params

# All test coroutines will be treated as marked
pytestmark = pytest.mark.asyncio


@pytest.fixture
def query_person_params() -> dict:
    """Дефолтные GET параметры для персонажей"""

    return {
        "query": "",
        "page_size": 50,
        "page_number": 1,
    }


class TestPerson:
    async def test_person_list_without_params(self, create_test_data, make_get_request, redis_client, settings,
                                              query_person_params):
        """Тест эндпоинта /person/search"""

        response = await make_get_request("/person/search")
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        response_with_page = await make_get_request("/person/search", params=query_person_params)
        assert response.body == response_with_page.body, \
            "Запрос без параметров должен соответствовать запросу с параметрами по умолчанию"
        assert await redis_client.get(
            get_redis_key_by_params(settings.PERSON_INDEX, query_person_params)), err.REDIS_404

    async def test_person_page_number_param(self, create_test_data, make_get_request, query_person_params, settings,
                                            redis_client):
        """Тест параметра ?page_number"""

        query_person_params["page_number"] = 2
        response = await make_get_request("/person/search", params=query_person_params)
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 50, err.WRONG_LEN
        assert isinstance(response.body, list), err.WRONG_RESPONSE_BODY
        assert await redis_client.get(get_redis_key_by_params(
            settings.PERSON_INDEX, query_person_params)), err.REDIS_404

        query_person_params["page_number"] = 1
        response_with_first_number = await make_get_request("/person/search", params=query_person_params)
        assert response_with_first_number.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response_with_first_number.body) == 50, err.WRONG_LEN
        assert isinstance(response_with_first_number.body, list), err.WRONG_RESPONSE_BODY
        assert response.body != response_with_first_number.body, "Значения 1-ой и 2-ой страницы не должны совпадать"

    async def test_person_page_number_param_page1M(self, create_test_data, make_get_request, query_person_params):
        query_person_params["page_number"] = 1_000_000
        response_with_big_page_number = await make_get_request("/person/search", params=query_person_params)
        assert response_with_big_page_number.status == HTTPStatus.UNPROCESSABLE_ENTITY, err.WRONG_GTE_PAGE_SIZE

    async def test_person_page_number_param_page0(self, create_test_data, make_get_request, query_person_params):
        query_person_params["page_number"] = 0
        response_with_zero_page_number = await make_get_request("/person/search", params=query_person_params)
        assert response_with_zero_page_number.status == HTTPStatus.UNPROCESSABLE_ENTITY, err.WRONG_LTE_PAGE_SIZE

    async def test_person_page_size_param(self, create_test_data, make_get_request, query_person_params, redis_client,
                                          settings):
        """Тест параметра ?page_size"""

        query_person_params["page_size"] = 51
        response = await make_get_request("/person/search", params=query_person_params)
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 51, err.WRONG_LEN
        assert await redis_client.get(
            get_redis_key_by_params(settings.PERSON_INDEX, query_person_params)), err.REDIS_404

    async def test_person_page_size_param_size1M(self, create_test_data, make_get_request, query_person_params):
        query_person_params["page_size"] = 1_000_000
        response_with_big_page_size = await make_get_request("/person/search", params=query_person_params)
        assert response_with_big_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY, err.WRONG_GTE_PAGE_SIZE

    async def test_person_page_size_param_size0(self, create_test_data, make_get_request, query_person_params):
        query_person_params["page_size"] = 0
        response_with_zero_page_size = await make_get_request("/person/search", params=query_person_params)
        assert response_with_zero_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY, err.WRONG_LTE_PAGE_SIZE

    async def test_person_by_id(self, create_test_data, make_get_request, settings, redis_client):
        """Тест эндпоинта /person/{person_id}"""

        existing_person = "a2815390-07d6-46a5-942e-24819250f2cb"
        response = await make_get_request(f"/person/{existing_person}")
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert isinstance(response.body, dict), err.WRONG_RESPONSE_BODY

        assert response.body.get("uuid") is not None, "У персонажа отсутствует uuid"
        assert await redis_client.get(settings.PERSON_INDEX + ":" + existing_person), err.REDIS_404

    async def test_person_by_id_nonexistent(self, create_test_data, make_get_request):
        nonexistent_person = "40415390-07d6-46a5-942e-24819250f2cb"
        response_for_nonexistent_person = await make_get_request(f"/film/{nonexistent_person}")
        assert response_for_nonexistent_person.status == HTTPStatus.NOT_FOUND, err.WRONG_STATUS

    async def test_person_search(self, create_test_data, make_get_request, query_person_params):
        """Тест энпоинта /person/search"""

        query_person_params["query"] = "FullName_98"
        response = await make_get_request("/person/search", params=query_person_params)
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 1, err.WRONG_LEN
        assert response.body[0]["uuid"] == "bddfebe2-abfb-4e2f-a49e-22b3d9818a2c", 'У персоны нет UUID'

    async def test_person_films(self, create_test_data, make_get_request, redis_client, settings, query_person_params):
        """ Тест person/<person_uuid>film/ """

        person_id = '72339735-edb6-4542-b272-df89b28a5338'
        response = await make_get_request(f"/person/{person_id}/film")
        assert response.status == HTTPStatus.OK, err.WRONG_STATUS
        assert len(response.body) == 6, err.WRONG_LEN
        assert redis_client.get(get_redis_key_by_params(settings.PERSON_INDEX, query_person_params)), err.REDIS_404
