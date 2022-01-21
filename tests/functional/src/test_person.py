from http import HTTPStatus

import pytest


# все граничные случаи по валидации данных;
# поиск конкретного человека;
# поиск всех фильмов с участием человека;
# вывести всех людей;
# поиск с учетом кеша в Redis.


class TestPerson:

    @pytest.mark.asyncio
    async def test_person_list_without_params(self, create_test_data, make_get_request):
        """Тест эндпоинта /person/search"""

        response = await make_get_request('/person/search')

        assert response.status == HTTPStatus.OK, "Неправильный статус ответа"

        response_with_page = await make_get_request('/person/search',
                params={
                    "page_size": "50",
                    "page_number": "1",
                    })
        assert response.body == response_with_page.body, 'Запрос без параметров должен соответствовать запросу с ' \
                                                        'параметрами по умолчанию'
