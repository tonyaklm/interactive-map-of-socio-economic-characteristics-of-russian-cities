from sqlalchemy import select, delete, update, func
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
import json
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Repository:
    """ Класс для шаблонных хождений в таблицу БД"""

    async def select_by_unique_column(self, table: Base, unique_column: str, unique_value: int,
                                      session: AsyncSession) -> json:
        """Makes select by given column names and expected values
        """

        items = select(table).where(getattr(table, unique_column) == unique_value)
        results = await session.execute(items)
        response_json = results.scalars().all()
        if not response_json:
            return {}
        return response_json[0]

    async def select_columns(self, table: Base, columns: list, indicator: str,
                             session: AsyncSession, summ=False) -> json:
        """Select specific columns"""
        agg_func = func.sum(getattr(table, indicator)).label(indicator) if summ else func.avg(
            getattr(table, indicator)).label(indicator)

        stmt = select(*[getattr(table, column) for column in columns],
                      agg_func,
                      func.min(table.id).label('min_municipality_id')).group_by(
            *[getattr(table, column) for column in columns])
        results = await session.execute(stmt)
        return results.all()

    async def select_mean_indicator(self, table: Base, columns: list, indicators: list, session: AsyncSession):
        agg_funcs = [func.avg(getattr(table, indicator)).label(indicator) for indicator in indicators]
        stmt = select(*[getattr(table, column) for column in columns],
                      *agg_funcs,
                      func.min(table.id).label('min_municipality_id')).group_by(
            *[getattr(table, column) for column in columns])
        results = await session.execute(stmt)
        return results.all()

    async def select_settlement_indicators(self, table: Base, columns: list, indicators: list, location_keys: list,
                                           location_values: str, session: AsyncSession):
        agg_funcs = [func.avg(getattr(table, indicator)).label(indicator) for indicator in indicators]
        stmt = select(*[getattr(table, column) for column in columns],
                      *agg_funcs,
                      func.min(table.id).label('min_municipality_id')).group_by(
            *[getattr(table, column) for column in location_keys]).where(
            *[getattr(table, location_keys[i]) == location_values[i] for i in range(len(location_keys))])
        results = await session.execute(stmt)
        return results.all()

    async def update_by_unique_column(self, table: Base, column: str, expected_value: Any, new_values: json,
                                      session: AsyncSession):
        """Updates item by its unique key"""
        stmt = update(table).where(getattr(table, column) == expected_value).values(new_values)
        results = await session.execute(stmt)
        return results.rowcount


repo = Repository()
