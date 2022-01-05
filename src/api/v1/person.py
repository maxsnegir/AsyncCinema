from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException, Response

from helpers.constants import ErrorMsg
from models.film import FilmShort
from models.person import Person
from services.film import get_film_service, FilmService
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/search', description='Поиск по персонам.')
async def person_search(query: str = Query(None, description='Поисковый запрос'),
                        page_size: int = Query(50, ge=1, lt=1000, description='Размер страницы'),
                        page_number: int = Query(1, ge=1, lt=1000, description='Номер страницы'),
                        person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    persons = await person_service.get_list(query=query, page_size=page_size, page_number=page_number)
    return persons


@router.get('/{person_id}', response_model=Person, description='Данные по персоне.')
async def person_detail(person_id: str,
                        person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMsg.PERSON_NOT_FOUND)
    return Person(**person.dict())


@router.get('/{person_id}/film', description='Фильмы по персоне.')
async def films_by_person(response: Response,
                          person_id: str,
                          page_size: int = Query(50, ge=1, lt=1000, description='Размер страницы'),
                          page_number: int = Query(1, ge=1, lt=1000, description='Номер страницы'),
                          person_service: FilmService = Depends(get_film_service)) -> List[FilmShort]:
    films = await person_service.get_list(page_size=page_size, page_number=page_number, person_id=person_id)
    response.headers["!DEPRECATED"] = "used for old android devices"
    return films
