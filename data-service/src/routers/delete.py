import os
from cache.maps import get_map
from fastapi import APIRouter, Request, status, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from utils.session import get_session
from fastapi import HTTPException
from utils.data import delete_indicator
from config import settings
from utils.data import get_indicator_names
from utils.feature_data import delete_feature
from models.user import UserData
from utils.auth import get_user

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/delete")


@router.get("/column")
async def get_delete_page(request: Request, session: AsyncSession = Depends(get_session), message: str = "",
                          color: str = None, user: UserData = Depends(get_user)):
    if not user.is_login or user.is_error:
        url = f'http://{settings.user_service_address}/login/'
        return RedirectResponse(url=url)
    indicator_names = await get_indicator_names(session)
    return templates.TemplateResponse(name="delete_column.html",
                                      context={"request": request,
                                               "columns": sorted(list(indicator_names)),
                                               "message": message,
                                               "color": color})


@router.post("/column")
async def delete_column(request: Request, column_name: str = Form(...),
                        session: AsyncSession = Depends(get_session),
                        user: UserData = Depends(get_user)):
    if not user.is_login or user.is_error:
        url = f'http://{settings.user_service_address}/login/'
        return RedirectResponse(url=url)
    indicator_names = await get_indicator_names(session)
    if column_name not in indicator_names:
        redirect_url = request.url_for('get_delete_page').include_query_params(
            message=f"Индикатора {column_name} не сущетвует",
            color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    try:
        await delete_feature(column_name, session)
        response = await delete_indicator(column_name, session)
    except HTTPException as e:
        redirect_url = request.url_for('get_delete_page').include_query_params(
            message=e.detail,
            color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    try:
        os.remove(get_map(column_name))
    except FileNotFoundError:
        pass

    redirect_url = request.url_for('get_delete_page').include_query_params(
        message=f"Индикатор {column_name} успешно удален",
        color="green")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)