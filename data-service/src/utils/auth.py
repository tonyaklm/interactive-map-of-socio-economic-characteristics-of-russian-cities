from http import HTTPStatus
from typing import Optional

from fastapi import Cookie
from models.user import UserData
import httpx
from config import settings


async def get_user(access_token_cookie: Optional[str] = Cookie(default=None)) -> UserData:
    href_token = "http://" + settings.user_service_address + "/get_token/"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(href_token, cookies={"access_token_cookie": access_token_cookie})
        except httpx.ConnectError:
            return UserData(is_login=False,
                            is_admin=False,
                            is_error=True)
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            return UserData(is_login=data.get('is_login', False),
                            is_admin=data.get('is_admin', False),
                            is_error=False)
        return UserData(is_login=False,
                        is_admin=False,
                        is_error=True)
