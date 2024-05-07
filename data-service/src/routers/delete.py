import pandas as pd
from fastapi import APIRouter, File, UploadFile, Request, status, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from utils.session import get_session
from fastapi import HTTPException
from utils.column import get_columns
from tables.data import DataDao
from utils.data import delete_indicator
from cache.cache_graphs import update_all_settlements

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/delete")


@router.get("/column")
async def get_delete_page(request: Request, session: AsyncSession = Depends(get_session), message: str = "",
                          color: str = None):
    columns = await get_columns(DataDao.__tablename__, session)
    column_names = list(columns.keys())[15:] + ['population', 'children']
    return templates.TemplateResponse(name="delete_column.html",
                                      context={"request": request,
                                               "columns": list(column_names),
                                               "message": message,
                                               "color": color})


@router.post("/column")
async def delete_column(request: Request, column_name: str = Form(...),
                        session: AsyncSession = Depends(get_session)):
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
