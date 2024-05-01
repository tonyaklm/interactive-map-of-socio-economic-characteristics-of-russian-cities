from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column
from sqlalchemy import types
from models import data_models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DataError, DBAPIError, ProgrammingError
from common.repository import repo
from tables.data import DataDao
from utils.session import get_session
from utils.column import add_column, get_columns
from utils.check_columns import check_columns
import json

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


@router.get("/", status_code=200, summary="Get all columns names", tags=['data'])
async def get_column_names(session: AsyncSession = Depends(get_session)):
    columns = await get_columns(DataDao.__tablename__, session)
    column_names = list(columns.keys())[15:]

    column_types = []
    for column in column_names:
        column_types.append(column.split('_')[0])
    return {'column_names': column_names,
            'column_types': column_types}


@router.get("/{indicator}", status_code=200, summary="Get data for indicator", tags=['data'])
async def get_indicator(indicator: str, session: AsyncSession = Depends(get_session)):
    await check_columns(session)
    selected_columns = ['region', 'settlement', 'longitude_dd', 'latitude_dd']

    summ_flag = True if indicator in ['population', 'children'] else False
    if indicator not in DataDao.__table__.columns.keys():
        raise HTTPException(status_code=404, detail={'no such indicator'})

    selected_data = await repo.select_columns(DataDao, selected_columns, indicator, session, summ=summ_flag)
    print(len([row._asdict() for row in selected_data]))
    return [row._asdict() for row in selected_data]
    # return [row._asdict() for row in selected_data]
