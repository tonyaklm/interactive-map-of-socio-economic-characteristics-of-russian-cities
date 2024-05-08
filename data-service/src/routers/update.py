import pandas as pd
from fastapi import APIRouter, File, UploadFile, Request, status, Depends, Form, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils.data import create_column, update_data
from sqlalchemy.ext.asyncio import AsyncSession
from utils.session import get_session
from io import BytesIO
from models.data_models import CreateColumn, UpdateData
from fastapi import HTTPException
from utils.column import get_columns
from tables.data import DataDao
from utils.convert_value import get_new_value
from models import graph_data
from cache.cache_maps import cache_map
from cache.cache_graphs import update_all_settlements, update_one_settlement
from common.repository import repo
from common.sqlalchemy_data_type import matching_columns, unupdateable_columns
from typing import Optional
import os
from jose import jwt
from config import settings

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/update")


@router.get("/column")
async def get_update_column(request: Request, message: str = "", color: str = None,
                            access_token_cookie: Optional[str] = Cookie(default=None)):
    if access_token_cookie == None:
        url = f'http://{settings.user_service_address}/login/'
        return RedirectResponse(url=url)
    if access_token_cookie != None:
        claims = jwt.get_unverified_claims(access_token_cookie)
        if not claims.get('is_admin'):
            url = f'http://{settings.user_service_address}/login/'
            return RedirectResponse(url=url)
    return templates.TemplateResponse(name="update_column.html",
                                      context={"request": request,
                                               "message": message,
                                               "color": color,
                                               "matching_columns": matching_columns,
                                               "unupdateable_columns": unupdateable_columns
                                               })


@router.get("/")
async def get_update_value(request: Request, message: str = "", color: str = None,
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
    column_names = set(columns.keys()).difference(unupdateable_columns)

    return templates.TemplateResponse(name="update_value.html",
                                      context={"request": request,
                                               "columns": list(column_names),
                                               "message": message,
                                               "color": color,
                                               "matching_columns": matching_columns,
                                               "unupdateable_columns": unupdateable_columns
                                               })


@router.post("/column")
async def update_column(request: Request, file: UploadFile = File(...),
                        session: AsyncSession = Depends(get_session),
                        access_token_cookie: Optional[str] = Cookie(default=None)):
    global new_data
    if access_token_cookie == None:
        url = f'http://{settings.user_service_address}/login/'
        return RedirectResponse(url=url)
    if access_token_cookie != None:
        claims = jwt.get_unverified_claims(access_token_cookie)
        if not claims.get('is_admin'):
            url = f'http://{settings.user_service_address}/login/'
            return RedirectResponse(url=url)
    if not file:
        redirect_url = request.url_for('get_update_column').include_query_params(message="Необходимо загрузить файл",
                                                                                 color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    if file.content_type != "text/csv":
        redirect_url = request.url_for('get_update_column').include_query_params(message="Формат файла должен быть csv",
                                                                                 color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    try:
        new_data = pd.read_csv(BytesIO(file.file.read()))
    except UnicodeDecodeError:
        error_message = "Невозможно распаковать файл, проверьте тип файла"
        redirect_url = request.url_for('get_update_column').include_query_params(message=error_message,
                                                                                 color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    if len(new_data.columns.values.tolist()) != 2:
        error_message = "В файле должно быть 2 колонки - с сопоставляющей конокой и новыми данными"
        redirect_url = request.url_for('get_update_column').include_query_params(message=error_message,
                                                                                 color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    error_message = None
    matching_column = new_data.columns.values.tolist()[0].strip()
    if matching_column not in matching_columns:
        error_message = f"""Сопостовляющая колонка должна быть одна из 
             {matching_columns}, введена {matching_column}"""
    columns = await get_columns(DataDao.__tablename__, session)
    column_names = set(columns.keys()).difference(unupdateable_columns)

    for column in new_data.columns.values.tolist()[1:]:
        if column in unupdateable_columns:
            error_message = f"""Колонка с обновляемыми данными не может быть ни одной из {unupdateable_columns}. \n
                                    Получена колонка {column}"""
            break
        if column not in column_names:
            error_message = f"""Колонка с обновляемыми данными должна быть среди существующих. \n
                                Колонки с имененим {column} не существует."""
            break
    if error_message:
        redirect_url = request.url_for('get_update_column').include_query_params(message=error_message,
                                                                                 color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    try:

        for column in new_data.columns.values.tolist()[1:]:
            for index, row in new_data.iterrows():
                await update_data(
                    UpdateData(matching_column_value=row[matching_column],
                               matching_column_name=matching_column,
                               column=column,
                               new_value=row[column]),
                    session)
    except HTTPException as e:
        await session.rollback()
        redirect_url = request.url_for('get_update_column').include_query_params(message=e.detail,
                                                                                 color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    await session.commit()

    for column in new_data.columns.values.tolist()[1:]:
        await cache_map(column, session)

    for index, row in new_data.iterrows():
        city = await repo.select_by_unique_column(DataDao, matching_column, row[matching_column], session)
        if city:
            await update_one_settlement(graph_data.UpdateGraphData(settlement=city.settlement,
                                                                   longitude_dd=city.longitude_dd,
                                                                   latitude_dd=city.latitude_dd))

    # await update_all_settlements()

    redirect_url = request.url_for('get_update_column').include_query_params(
        message=f"Колонки {list(new_data.columns.values.tolist()[1:])} успешно обновлены",
        color="green")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/")
async def update_value(request: Request, column_name: str = Form(...), matching_column: str = Form(...),
                       matching_value: float = Form(...), new_value: str = Form(...), new_value_type: str = Form(...),
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
    error_message = None
    if matching_column not in matching_columns:
        error_message = f"""Сопостовляющая колонка должна быть одна из 
                 {matching_columns}, введена {matching_column}"""
    columns = await get_columns(DataDao.__tablename__, session)
    column_names = set(columns.keys()).difference(unupdateable_columns)

    if column_name in unupdateable_columns:
        error_message = f"""Колонка с обновляемыми данными не может быть ни одной из {unupdateable_columns}\n
                                    Получена колонка {column_name}"""
    if column_name not in column_names:
        error_message = f"""Колонка с обновляемыми данными должна быть среди существующих.\n
                                Колонки с имененим {column_name} не существует.\n
                                Вы можете повторить запрос для других колонок."""

    if error_message:
        redirect_url = request.url_for('get_update_value').include_query_params(message=error_message,
                                                                                color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    converted_new_value = get_new_value(new_value, new_value_type)
    try:
        await update_data(
            UpdateData(matching_column_value=matching_value,
                       matching_column_name=matching_column,
                       column=column_name,
                       new_value=converted_new_value),
            session)
    except HTTPException as e:
        await session.rollback()
        redirect_url = request.url_for('get_update_value').include_query_params(message=e.detail,
                                                                                color="red")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    await session.commit()

    await cache_map(column_name, session)

    city = await repo.select_by_unique_column(DataDao, matching_column, matching_value, session)
    if city:
        await update_one_settlement(graph_data.UpdateGraphData(settlement=city.settlement,
                                                               longitude_dd=city.longitude_dd,
                                                               latitude_dd=city.latitude_dd))

    redirect_url = request.url_for('get_update_value').include_query_params(
        message=f"""Для {column_name} с {matching_column}={matching_value}"
                 успешно установлено новое значение {new_value}""",
        color="green")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
