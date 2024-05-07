import pandas as pd
from fastapi import APIRouter, File, UploadFile, Request, status, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from utils.session import get_session
from fastapi import HTTPException, Cookie
from utils.column import get_columns
from tables.data import DataDao
from utils.data import delete_indicator
from cache.cache_graphs import update_all_settlements
from typing import Optional
import os
from jose import jwt

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/delete")


@router.get("/column")
async def get_delete_page(request: Request, session: AsyncSession = Depends(get_session), message: str = "",
                          color: str = None, access_token_cookie: Optional[str] = Cookie(default=None)):
    if access_token_cookie == None:
        url = f'http://{os.getenv("INTERNAL_ADDRESS")}:{os.getenv("USER_SERVICE_PORT")}/login/'
        return RedirectResponse(url=url)
    if access_token_cookie != None:
        claims = jwt.get_unverified_claims(access_token_cookie)
        if not claims.get('is_admin'):
            url = f'http://{os.getenv("INTERNAL_ADDRESS")}:{os.getenv("USER_SERVICE_PORT")}/login/'
            return RedirectResponse(url=url)
    columns = await get_columns(DataDao.__tablename__, session)
    column_names = list(columns.keys())[15:]
    return templates.TemplateResponse(name="delete_column.html",
                                      context={"request": request,
                                               "columns": list(column_names),
                                               "message": message,
                                               "color": color})


@router.post("/column")
async def delete_column(request: Request, column_name: str = Form(...),
                        session: AsyncSession = Depends(get_session),
                        access_token_cookie: Optional[str] = Cookie(default=None)):
    if access_token_cookie == None:
        url = f'http://{os.getenv("INTERNAL_ADDRESS")}:{os.getenv("USER_SERVICE_PORT")}/login/'
        return RedirectResponse(url=url)
    if access_token_cookie != None:
        claims = jwt.get_unverified_claims(access_token_cookie)
        if not claims.get('is_admin'):
            url = f'http://{os.getenv("INTERNAL_ADDRESS")}:{os.getenv("USER_SERVICE_PORT")}/login/'
            return RedirectResponse(url=url)
    columns = await get_columns(DataDao.__tablename__, session)
    column_names = list(columns.keys())[15:]
    if column_name not in column_names:
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

    await update_all_settlements()
    redirect_url = request.url_for('get_delete_page').include_query_params(
        message=f"Колонка {column_name} успешно удалена",
        color="green")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
