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

        response_with_page = await make_get_request('/film',
                                                    params={
                                                        "sort": "-imdb_rating",
                                                        "page_size": "50",
                                                        "page_number": "1",
                                                        "filter_genre": ""
                                                    })
        assert response.body == response_with_page.body, 'Запрос без параметров должен соответствовать запросу с ' \
                                                         'параметрами по умолчанию'

    @pytest.mark.asyncio
    async def test_film_sort_param(self, create_test_data, make_get_request):
        """Тест параметра ?sort"""
        response_by_desc_sort = await make_get_request('/film')
        assert response_by_desc_sort.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response_by_desc_sort.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response_by_desc_sort.body, list), "Неправильный тип данных в ответе"

        sorted_by_desc = sorted(response_by_desc_sort.body, key=lambda film: film["imdb_rating"], reverse=True)
        assert sorted_by_desc == response_by_desc_sort.body, "Фильмы не отсортированы уменьшению рейтинга"

        response_by_asc_sort = await make_get_request('/film', params={"sort": "imdb_rating"})
        assert response_by_asc_sort.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response_by_asc_sort.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response_by_asc_sort.body, list), "Неправильный тип данных в ответе"

        sorted_by_asc = sorted(response_by_asc_sort.body, key=lambda film: film["imdb_rating"], reverse=False)
        assert response_by_asc_sort.body == sorted_by_asc, 'Фильмы должны возвращаться по возрастанию рейтинга'

    @pytest.mark.asyncio
    async def test_film_page_number_param(self, create_test_data, make_get_request):
        """Тест параметра ?page_number"""

        response = await make_get_request('/film', params={"page_number": 2})
        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response.body) == 50, "Неправильное количество фильмов"
        assert isinstance(response.body, list), "Неправильный тип данных в ответе"

        response_with_first_number = await make_get_request('/film', params={"page_number": 1})
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
    async def test_fim_page_size_param(self, create_test_data, make_get_request):
        """Тест параметра ?page_size"""

        response = await make_get_request('/film', params={"page_size": 51})
        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response.body) == 51, "Неправильное количество фильмов"

        response_with_zero_page_size = await make_get_request('/film', params={"page_size": 0})
        assert response_with_zero_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для размера страницы == 0'

        response_with_large_page_size = await make_get_request('/film', params={"page_size": 1000000})
        assert response_with_large_page_size.status == HTTPStatus.UNPROCESSABLE_ENTITY, \
            'Неправильный статус ответа для размера страницы > 1000'

    @pytest.mark.asyncio
    async def test_film_filter_genre_param(self, create_test_data, make_get_request):
        """Тест параметра ?filter_genre"""

        existing_genre_id = '949386de-246e-4b8c-9968-257309c2e52b'
        response = await make_get_request('/film', params={"filter_genre": existing_genre_id})

        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert len(response.body) == 6, 'Должно быть 6 :)'

        nonexistent_genre_id = 'ec2cd0db-fdfd-4e12-87a5-ac3a93c0398f'
        response_with_nonexistent_genre = await make_get_request('/film',
                                                                 params={"filter_genre": nonexistent_genre_id}
                                                                 )
        assert response_with_nonexistent_genre.status == HTTPStatus.OK, "Неверный статус ответа"
        assert len(response_with_nonexistent_genre.body) == 0, "Неверное количество фильмов"

    @pytest.mark.asyncio
    async def test_film_by_id(self, create_test_data, make_get_request):
        """Тест эндопинта film/{film_id}"""

        existing_film = 'e6ddc3ce-6945-4a9e-b0d1-31b2ae39ffd8'
        response = await make_get_request(f'/film/{existing_film}')
        assert response.status == HTTPStatus.OK, 'Неправильный статус ответа'
        assert isinstance(response.body, dict), 'Возвращается неправильный формат фильма'
        assert response.body.get("uuid") is not None, 'У фильма отсутствует uuid'

        nonexistent_film = 'ec2cd0db-fdfd-4e12-87a5-ac3a93c0398f'
        response_for_nonexistent_film = await make_get_request(f'/film/{nonexistent_film}')
        assert response_for_nonexistent_film.status == HTTPStatus.NOT_FOUND, 'Неправильный статус ответа'

