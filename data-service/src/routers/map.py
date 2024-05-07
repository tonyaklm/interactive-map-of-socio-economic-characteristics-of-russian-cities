from typing import Optional

from fastapi import APIRouter, Request, Depends, Query, status, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils.data import get_column_names, get_indicator
from utils.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from cache.maps import get_map
import time
from jose import jwt
import os

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix='/map')


@router.get("/")
async def render_map(request: Request, session: AsyncSession = Depends(get_session),
                     access_token_cookie: Optional[str] = Cookie(default=None)):
    start = time.time()
    columns = await get_column_names(session)

    is_admin = False
    is_login = False
    if access_token_cookie != None:
        claims = jwt.get_unverified_claims(access_token_cookie)
        is_admin = claims['is_admin']
        is_login = True

    href_login = "http://" + os.getenv('INTERNAL_ADDRESS') + ":" + os.getenv('USER_SERVICE_PORT') + "/login/"
    href_logout = "http://" + os.getenv('INTERNAL_ADDRESS') + ":" + os.getenv('USER_SERVICE_PORT') + "/logout/"
    href_register = "http://" + os.getenv('INTERNAL_ADDRESS') + ":" + os.getenv('USER_SERVICE_PORT') + "/register/"
    resp = templates.TemplateResponse(name="index.html",
                                      context={"request": request, "columns": columns['column_names'],
                                               "groups": columns['column_types'],
                                               "template_name": get_map("Empty_Map"), "selected": "Empty Map"
                                          , "is_login": is_login, "is_admin": is_admin, "href_login": href_login,
                                               "href_logout": href_logout, "href_register": href_register})

    print(time.time() - start)

    return resp


@router.get('/indicator')
async def chosen_indicator(request: Request, indicator: str = Query(...), session: AsyncSession = Depends(get_session), access_token_cookie: Optional[str] = Cookie(default=None)):
    input_indicator = indicator
    if indicator in ['Population', 'Children']:
        indicator = indicator.lower()
    elif indicator == 'Empty Map':
        indicator = 'Empty_Map'

    columns = await get_column_names(session)

    is_admin = False
    is_login = False
    if access_token_cookie != None:
        claims = jwt.get_unverified_claims(access_token_cookie)
        is_admin = claims['is_admin']
        is_login = True

    href_login = "http://" + os.getenv('INTERNAL_ADDRESS') + ":" + os.getenv('USER_SERVICE_PORT') + "/login/"
    href_logout = "http://" + os.getenv('INTERNAL_ADDRESS') + ":" + os.getenv('USER_SERVICE_PORT') + "/logout/"
    href_register = "http://" + os.getenv('INTERNAL_ADDRESS') + ":" + os.getenv('USER_SERVICE_PORT') + "/register/"

    if indicator not in ['population', 'children', 'Empty_Map'] + columns['column_names']:
        return RedirectResponse(url="/map", status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(name="index.html",
                                      context={"request": request, "columns": columns['column_names'],
                                               "groups": columns['column_types'], "selected": input_indicator,
                                               "template_name": get_map(indicator), "is_login": is_login,
                                               "is_admin": is_admin, "href_login": href_login,
                                               "href_logout": href_logout, "href_register": href_register})
