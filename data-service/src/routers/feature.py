from fastapi import APIRouter, Request, status, Depends, Form, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from utils.session import get_session
from typing import Optional
from jose import jwt
from config import settings
from utils.description import get_indicator_types
from utils.feature_data import update_feature_description
from models.user import UserData
from utils.auth import get_user

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/feature")


@router.get("/description")
async def get_update_description(request: Request, message: str = "", color: str = None,
                                 session: AsyncSession = Depends(get_session),
                                 user: UserData = Depends(get_user)):
    if not user.is_login or user.is_error:
        url = f'http://{settings.user_service_address}/login/'
        return RedirectResponse(url=url)

    indicator_types = await get_indicator_types(session)
    return templates.TemplateResponse(name="description.html",
                                      context={"request": request,
                                               "message": message,
                                               "color": color,
                                               "indicator_types": indicator_types
                                               })


@router.post("/description")
async def update_description(request: Request, indicator: str = Form(...), description: str = Form(""),
                             session: AsyncSession = Depends(get_session),
                             user: UserData = Depends(get_user)):
    if not user.is_login or user.is_error:
        url = f'http://{settings.user_service_address}/login/'
        return RedirectResponse(url=url)

    error_message = None

    indicator_types = await get_indicator_types(session)
    try:
        indicator_types.remove('Empty_Map')
    except ValueError:
        pass
    if indicator not in indicator_types:
        error_message = f"""Индикатор должен быть одним из {indicator_types}, получен {indicator}"""
    if len(description) > 100:
        error_message = f"Допустимая длина описания = 100 символов"

    if error_message:
        redirect_url = request.url_for('get_update_description').include_query_params(message=error_message,
                                                                                      color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    if not await update_feature_description(indicator, description, session):
        redirect_url = request.url_for('get_update_description').include_query_params(message="Не получилось обновить",
                                                                                      color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    redirect_url = request.url_for('get_update_description').include_query_params(
        message=f"""Описание индикатора {indicator} успешно изменено""",
        color="green")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
