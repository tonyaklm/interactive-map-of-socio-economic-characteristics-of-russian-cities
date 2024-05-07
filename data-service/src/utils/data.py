from fastapi import HTTPException
from sqlalchemy import Column
from sqlalchemy import types
from models import data_models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DataError, DBAPIError, ProgrammingError, InvalidRequestError
from common.repository import repo
from tables.data import DataDao
from utils.column import add_column, get_columns, delete_column
from utils.check_columns import check_columns


async def update_data(update_data: data_models.UpdateData,
                      session: AsyncSession):
    try:
        rowcount = await repo.update_by_unique_column(DataDao, update_data.matching_column_name,
                                                      update_data.matching_column_value,
                                                      {update_data.column: update_data.new_value},
                                                      session)
    except DBAPIError or DataError:
        raise HTTPException(status_code=400,
                            detail=f"""Неверный тип данных для {update_data.column}\n\n
                            Проверьте тип данных и повторите операцию.""")
    if not rowcount:
        raise HTTPException(status_code=404,
                            detail=f"Не существует {update_data.matching_column_name}={update_data.matching_column_value}")


async def create_column(new_column: data_models.CreateColumn,
                        session: AsyncSession):
    try:
        setattr(DataDao, new_column.column_name,
                Column(new_column.column_name, getattr(types, new_column.column_type)))
    except InvalidRequestError:
        raise HTTPException(status_code=400, detail=f'''Колонка {new_column.column_name} уже существует.
                                                     Используйте метод "Обновить данные"''')
    try:
        await add_column('data', new_column.column_name, new_column.column_type, session)
    except ProgrammingError:
        raise HTTPException(status_code=400, detail=f'''Колонка {new_column.column_name} уже существует.
                                                     Используйте метод "Обновить данные"''')


async def get_column_names(session: AsyncSession):
    columns = await get_columns(DataDao.__tablename__, session)
    column_names = list(columns.keys())[15:]

    column_types = []
    for column in column_names:
        column_types.append(column.split('_')[0])
    return {'column_names': column_names,
            'column_types': column_types}


async def get_indicator(indicator: str, session: AsyncSession):
    await check_columns(session)
    selected_columns = ['region', 'settlement', 'longitude_dd', 'latitude_dd']

    summ_flag = True if indicator in ['population', 'children'] else False
    if indicator not in DataDao.__table__.columns.keys():
        raise HTTPException(status_code=404, detail={'no such indicator'})
    selected_data = await repo.select_columns(DataDao, selected_columns, indicator, session, summ=summ_flag)
    return [row._asdict() for row in selected_data]


async def delete_indicator(indicator: str, session: AsyncSession):
    try:
        del DataDao.__mapper__._props[indicator]
    except InvalidRequestError:
        raise HTTPException(status_code=404, detail=f"Колонки {indicator} не сущетсвует")
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Колонки {indicator} не сущетсвует")
    try:
        await delete_column(DataDao.__tablename__, indicator, session)
    except ProgrammingError:
        raise HTTPException(status_code=404, detail=f"Колонки {indicator} не сущетсвует")
