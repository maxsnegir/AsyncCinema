from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from helpers.auth import role_permission
from helpers.constants import ErrorMsg
from models.film import Film, FilmShort
from services.film import get_film_service, FilmService

router = APIRouter()


@router.get('/search', description='Полнотекстовый поиск по кинопроизведениям.', summary="Поиск кинопроизведений",
            response_description="Название и рейтинг фильма")
async def film_list_by_search(page_size: int = Query(50, ge=1, lt=1000, description='Размер страницы'),
                              page_number: int = Query(1, ge=1, lt=1000, description='Номер страницы'),
                              query: str = Query(None, description='Поисковый запрос'),
                              film_service: FilmService = Depends(get_film_service)) -> List[FilmShort]:
    films = await film_service.get_list(page_size=page_size, page_number=page_number, query=query)
    return films


@router.get('/{film_id}', response_model=Film, description='Полная информация по фильму.',
            summary="Поиск кинопроизведения")
@role_permission("user")
async def film_details(request: Request, film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMsg.FILM_NOT_FOUND)
    return Film(**film.dict())


@router.get('/', description='Список фильмов', summary='Список фильмов с пагинацией')
async def film_list(sort: str = Query("-imdb_rating", description='Параметр сортировки'),
                    page_size: int = Query(50, ge=1, lt=1000, description='Размер страницы'),
                    page_number: int = Query(1, ge=1, lt=1000, description='Номер страницы'),
                    filter_genre: str = Query("", description='Фильтр по жанру'),
                    film_service: FilmService = Depends(get_film_service)) -> List[FilmShort]:
    films = await film_service.get_list(sort=sort, page_size=page_size, page_number=page_number,
                                        filter_genre=filter_genre)
    return films
