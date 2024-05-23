from common.sqlalchemy_data_type import sqlalchemy_type
from fastapi import HTTPException
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from tables.data import DataDao
from utils.column import get_columns
from sqlalchemy import Column, types
from sqlalchemy.ext.asyncio import AsyncSession


async def check_columns(session: AsyncSession):
    try:
        real_columns = await get_columns(DataDao.__tablename__, session)
    except ProgrammingError:
        raise HTTPException(status_code=400, detail=f"Ошибка подключения")
    declarative_names = set(DataDao.__table__.columns.keys())
    real_names = set(real_columns.keys())

    if real_names.difference(declarative_names):
        column_type = {}
        for el in real_columns.cursor.description:
            column_type[el[0]] = sqlalchemy_type[el[1]]

        for column in real_names.difference(declarative_names):
            setattr(DataDao, column,
                    Column(column, getattr(types, column_type[column])))
    if declarative_names.difference(real_names):
        for column in declarative_names.difference(real_names):
            try:
                del DataDao.__mapper__._props[column]
            except InvalidRequestError:
                raise HTTPException(status_code=404, detail=f"Колонки {column} не сущетсвует")
            except KeyError:
                raise HTTPException(status_code=404, detail=f"Колонки {column} не сущетсвует")
