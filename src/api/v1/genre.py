from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from helpers.constants import ErrorMsg
from models.genre import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}', response_model=Genre, description='Данные по конкретному жанру.')
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMsg.GENRE_NOT_FOUND)

    return genre


@router.get('/', description='Список жанров.')
async def genre_list(page_size: int = Query(50, ge=1, lt=200, description='Размер страницы'),
                     page_number: int = Query(1, ge=1, lt=1000, description='Номер страницы'),
                     genre_service: GenreService = Depends(get_genre_service)) -> List[Genre]:

    genres = await genre_service.get_list(page_size=page_size, page_number=page_number)
    return genres
