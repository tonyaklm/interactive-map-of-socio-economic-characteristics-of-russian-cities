import os
from cache.maps import get_map
from fastapi import APIRouter, Request, status, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from utils.session import get_session
from fastapi import HTTPException, Cookie
from utils.data import delete_indicator
from typing import Optional
from jose import jwt
from config import settings
from utils.data import get_indicator_names
from utils.feature_data import delete_feature

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/delete")


@router.get("/column")
async def get_delete_page(request: Request, session: AsyncSession = Depends(get_session), message: str = "",
                          color: str = None, access_token_cookie: Optional[str] = Cookie(default=None)):
    if access_token_cookie == None:
        url = f'http://{settings.user_service_address}/login/'
        return RedirectResponse(url=url)
    if access_token_cookie != None:
        claims = jwt.get_unverified_claims(access_token_cookie)
        if not claims.get('is_admin'):
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
                        access_token_cookie: Optional[str] = Cookie(default=None)):
    if access_token_cookie == None:
        url = f'http://{settings.user_service_address}/login/'
        return RedirectResponse(url=url)
    if access_token_cookie != None:
        claims = jwt.get_unverified_claims(access_token_cookie)
        if not claims.get('is_admin'):
            url = f'http://{settings.user_service_address}/login/'
            return RedirectResponse(url=url)
    indicator_names = await get_indicator_names(session)
    if column_name not in indicator_names:
        redirect_url = request.url_for('get_delete_page').include_query_params(
            message=f"Колонки {column_name} не сущетсвует",
            color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    try:
        response = await delete_indicator(column_name, session)
    except HTTPException as e:
        redirect_url = request.url_for('get_delete_page').include_query_params(
            message=e.detail,
            color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    await delete_feature(column_name, session)

    try:
        os.remove(get_map(column_name))
    except FileNotFoundError:
        pass

    redirect_url = request.url_for('get_delete_page').include_query_params(
        message=f"Колонка {column_name} успешно удалена",
        color="green")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
