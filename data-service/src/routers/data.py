from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column
from sqlalchemy import types
from models import data_models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DataError, DBAPIError, ProgrammingError
from common.Repository import repo
from tables.DataDao import DataDao
from utils.session import get_session
from utils.add_column import add_column


router = APIRouter(prefix='/data')


@router.put("/", status_code=200, summary="Update data by its id", tags=['data'])
async def update_data(update_data: data_models.UpdateData,
                      session: AsyncSession = Depends(get_session)):
    try:
        await repo.update_by_criteria(DataDao, "id", update_data.data_id, {
            update_data.column: update_data.new_value
        }, session)
    except DBAPIError or DataError:
        raise HTTPException(status_code=400, detail="Передан неверный тип данных")

    return {}


@router.post("/create", status_code=200, summary="Create new column", tags=['data'])
async def create_column(new_column: data_models.CreateColumn,
                      session: AsyncSession = Depends(get_session)):

    setattr(DataDao, new_column.column_name,
            Column(new_column.column_name, getattr(types, new_column.column_type)))
    try:
        await add_column('data', new_column.column_name, new_column.column_type, session)
    except ProgrammingError:
        raise HTTPException(status_code=400, detail="Не получилось создать")
    return {}
