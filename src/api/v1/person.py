from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from models.person import Person
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return person


@router.get('/')
async def person_list(sort: str = Query(None, description='Параметр сортировки'),
                      page_size: int = Query(50, ge=1, le=200, description='Размер страницы'),
                      page_number: int = Query(1, ge=1, description='Номер страницы'),
                      filter_role: List[str] = Query(None, description='Фильтр по ролям'),
                      person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    persons = await person_service.get_list(sort, page_size, page_number, filter_role)
    if not persons:
        return []
    return persons
