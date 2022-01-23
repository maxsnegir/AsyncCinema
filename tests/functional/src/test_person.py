from http import HTTPStatus

import pytest

from ..utils.helper import get_redis_key_by_params


@pytest.fixture
def query_person_params() -> dict:
    """Дефолтные GET параметры для персонажей"""

    return {
        "query": "",
        "page_size": 50,
        "page_number": 1,
    }


class TestPerson:
    @pytest.mark.asyncio
    async def test_person_list_without_params(
        self,
        create_test_data,
        make_get_request,
        redis_client,
        query_person_params,
        settings,
    ):
        """Тест эндпоинта /person/search"""
        response = await make_get_request("/person/search")
        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        response_with_page = await make_get_request(
            "/person/search", params=query_person_params
        )
        assert (
            response.body == response_with_page.body
        ), "Запрос без параметров должен соответствовать запросу с параметрами по умолчанию"
        assert await redis_client.get(
            get_redis_key_by_params(settings.PERSON_INDEX, query_person_params)
        ), "Отсутствуют данные в redis"

    @pytest.mark.asyncio
    async def test_person_page_number_param(
        self,
        create_test_data,
        make_get_request,
        query_person_params,
        redis_client,
        settings,
    ):
        """Тест параметра ?page_number"""
        query_person_params["page_number"] = 2
        response = await make_get_request("/person/search", params=query_person_params)
        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        assert len(response.body) == 50, "Неправильное количество персонажей"
        assert isinstance(response.body, list), "Неправильный тип данных в ответе"
        assert await redis_client.get(
            get_redis_key_by_params(settings.PERSON_INDEX, query_person_params)
        ), "Отсутствуют данные в redis"
        query_person_params["page_number"] = 1
        response_with_first_number = await make_get_request(
            "/person/search", params=query_person_params
        )
        assert (
            response_with_first_number.status == HTTPStatus.OK
        ), "Неправильный статус ответа"
        assert (
            len(response_with_first_number.body) == 50
        ), "Неправильное количество персонажей"
        assert isinstance(
            response_with_first_number.body, list
        ), "Неправильный тип данных в ответе"
        assert (
            response.body != response_with_first_number.body
        ), "Значения 1-ой и 2-ой страницы не должны совпадать"
        query_person_params["page_number"] = 1_000_000
        response_with_big_page_number = await make_get_request(
            "/person/search", params=query_person_params
        )
        assert (
            response_with_big_page_number.status == HTTPStatus.UNPROCESSABLE_ENTITY
        ), "Неправильный статус ответа для номера страницы со значением больше миллиона"
        query_person_params["page_number"] = 0
        response_with_zero_page_number = await make_get_request(
            "/person/search", params=query_person_params
        )
        assert (
            response_with_zero_page_number.status == HTTPStatus.UNPROCESSABLE_ENTITY
        ), "Неправильный статус ответа для номера страницы со значением 0"

    @pytest.mark.asyncio
    async def test_person_page_size_param(
        self,
        create_test_data,
        make_get_request,
        query_person_params,
        redis_client,
        settings,
    ):
        """Тест параметра ?page_size"""
        query_person_params["page_size"] = 51
        response = await make_get_request("/person/search", params=query_person_params)
        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        assert len(response.body) == 51, "Неправильное количество персонажей"
        assert await redis_client.get(
            get_redis_key_by_params(settings.PERSON_INDEX, query_person_params)
        ), "Отсутствуют данные в redis"
        query_person_params["page_size"] = 1_000_000
        response_with_big_page_size = await make_get_request(
            "/person/search", params=query_person_params
        )
        assert (
            response_with_big_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY
        ), "Неправильный статус ответа для размера страницы со значением больше миллиона"
        query_person_params["page_size"] = 0
        response_with_zero_page_size = await make_get_request(
            "/person/search", params=query_person_params
        )
        assert (
            response_with_zero_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY
        ), "Неправильный статус ответа для размера страницы со значением 0"

    @pytest.mark.asyncio
    async def test_person_by_id(
        self, create_test_data, make_get_request, settings, redis_client
    ):
        """Тест эндпоинта /person/{person_id}"""
        existing_person = "a2815390-07d6-46a5-942e-24819250f2cb"
        response = await make_get_request(f"/person/{existing_person}")
        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        assert isinstance(
            response.body, dict
        ), "Возвращается неправильный формат персонажа"
        assert response.body.get("uuid") is not None, "У персонажа отсутствует uuid"
        assert await redis_client.get(
            settings.PERSON_INDEX + ":" + existing_person
        ), "Отсутствуют данные в redis"
        nonexistent_person = "404aaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        response_for_nonexistent_person = await make_get_request(
            f"/film/{nonexistent_person}"
        )
        assert (
            response_for_nonexistent_person.status == HTTPStatus.NOT_FOUND
        ), "Неправильный статус ответа"

    @pytest.mark.asyncio
    async def test_person_search(self, create_test_data, make_get_request):
        """Тест энпоинта /person/search"""
        response = await make_get_request("/person/search", {"query": "FullName_98"})
        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"
        assert len(response.body) == 1, "Неправильное количество персонажей"
        assert response.body[0]["uuid"] == "bddfebe2-abfb-4e2f-a49e-22b3d9818a2c"
