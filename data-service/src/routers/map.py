from typing import Optional

from fastapi import APIRouter, Request, Depends, Query, status, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from cache.maps import get_map
from config import settings
from utils.data import get_indicator_names
from utils.description import get_indicator_types, get_descriptions, get_drawable_columns, get_drawable_values
from models.user import UserData
from utils.auth import get_user

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix='/map')

@router.get("/")
async def render_map(request: Request, session: AsyncSession = Depends(get_session),
                     user: UserData = Depends(get_user)):
    href_login = "http://" + settings.user_service_address + "/login/"
    href_logout = "http://" + settings.user_service_address + "/logout/"
    href_register = "http://" + settings.user_service_address + "/register/"
    href_change_password = "http://" + settings.user_service_address + "/change_password/"

    indicator_types = await get_indicator_types(session)
    descriptions = await get_descriptions(session)
    drawable_columns = await get_drawable_columns(session)
    drawable_values = await get_drawable_values(session)

    return templates.TemplateResponse(name="index.html",
                                      context={"request": request,
                                               "indicator_types": indicator_types,
                                               "descriptions": descriptions,
                                               "drawable_columns": drawable_columns,
                                               "drawable_values": drawable_values,
                                               "selected_indicator": "Empty_Map",
                                               "template_name": get_map("Empty_Map"),
                                               "is_login": user.is_login,
                                               "is_admin": user.is_admin,
                                               "href_login": href_login,
                                               "href_logout": href_logout, "href_register": href_register,
                                               "href_change_password" : href_change_password})


@router.get('/indicator')
async def chosen_indicator(request: Request, indicator: str = Query(...), year: Optional[str] = Query(None),
                           session: AsyncSession = Depends(get_session),
                           user: UserData = Depends(get_user)):
    indicator_names = await get_indicator_names(session)
    indicator_names.add('Empty_Map')
    indicator_with_year = indicator + "_" + year if year else indicator

    href_login = "http://" + settings.user_service_address + "/login/"
    href_logout = "http://" + settings.user_service_address + "/logout/"
    href_register = "http://" + settings.user_service_address + "/register/"
    href_change_password = "http://" + settings.user_service_address + "/change_password/"

    if indicator_with_year not in indicator_names:
        return RedirectResponse(url="/map", status_code=status.HTTP_404_NOT_FOUND)

    indicator_types = await get_indicator_types(session)
    descriptions = await get_descriptions(session)
    drawable_columns = await get_drawable_columns(session)
    drawable_values = await get_drawable_values(session)

    return templates.TemplateResponse(name="index.html",
                                      context={"request": request,
                                               "indicator_types": indicator_types,
                                               "descriptions": descriptions,
                                               "drawable_columns": drawable_columns,
                                               "drawable_values": drawable_values,
                                               "selected_indicator": indicator,
                                               "selected_year": year,
                                               "template_name": get_map(indicator_with_year),
                                               "is_login": user.is_login,
                                               "is_admin": user.is_admin, "href_login": href_login,
                                               "href_logout": href_logout, "href_register": href_register,
                                               "href_change_password" : href_change_password})

@router.get("/info")
async def render_info(request: Request, session: AsyncSession = Depends(get_session)):
    return templates.TemplateResponse(name="info.html", context={"request": request})