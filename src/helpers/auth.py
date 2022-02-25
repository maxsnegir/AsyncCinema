from functools import wraps
import requests
from http import HTTPStatus

from fastapi import HTTPException
import aiohttp


def role_permission(role_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")

            session = aiohttp.ClientSession()
            async with session.get("http://host.docker.internal:82/api/v1/me", headers=request.headers) as response:
                data = await response.json()
                status_code = response.status

            if status_code != HTTPStatus.OK:
                raise HTTPException(status_code=status_code, detail=response.json())

            roles = data.get("roles")
            if role_name not in roles:
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Permission denied")

            return await func(*args, **kwargs)

        return wrapper

    return decorator
