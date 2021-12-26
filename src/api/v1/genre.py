import uuid
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from models.genre import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return genre


@router.get('/')
async def genre_list(sort: str = Query(None, description='Параметр сортировки'),
                     page_size: int = Query(50, ge=1, le=200, description='Размер страницы'),
                     page_number: int = Query(1, ge=1, description='Номер страницы'),
                     genre_service: GenreService = Depends(get_genre_service)) -> List[Genre]:
    genres = await genre_service.get_list(sort, page_size, page_number)
    if not genres:
        return []
    return genres
