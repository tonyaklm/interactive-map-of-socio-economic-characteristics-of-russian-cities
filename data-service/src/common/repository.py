from sqlalchemy import select, update, func, delete
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
                             session: AsyncSession, agg_func: str) -> json:
        """Select specific columns"""
        agg_func = getattr(func, agg_func)(getattr(table, indicator)).label(indicator)

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

    async def select_settlement_indicators(self, table: Base, indicators: list, location_keys: list,
                                           location_values: str, session: AsyncSession):
        agg_funcs = [func.avg(getattr(table, indicator)).label(indicator) for indicator in indicators]
        stmt = select(*agg_funcs).group_by(
            *[getattr(table, column) for column in location_keys]).where(
            *[getattr(table, location_keys[i]) == location_values[i] for i in range(len(location_keys))])
        results = await session.execute(stmt)
        return results.all()

    async def select_region_indicators(self, table: Base, indicators: list, location_keys: list,
                                       region_key: str, region_value: int, agg_func: str, session: AsyncSession):
        sub_agg_funcs = [getattr(func, agg_func)(getattr(table, indicator)).label(indicator) for indicator in
                         indicators]
        sub_query = (
            select(*sub_agg_funcs, getattr(table, region_key)).group_by(
                *[getattr(table, column) for column in location_keys], getattr(table, region_key)).alias()
        )

        agg_funcs = [func.avg(getattr(sub_query.columns, f"{indicator}")).label(f"{indicator}_1") for indicator in
                     indicators]
        stmt = (
            select(*agg_funcs).group_by(
                getattr(sub_query.columns, region_key)).where(
                getattr(sub_query.columns, region_key) == region_value)
        )

        results = await session.execute(stmt)
        return results.all()

    async def update_by_unique_column(self, table: Base, column: str, expected_value: Any, new_values: json,
                                      session: AsyncSession):
        """Updates item by its unique key"""
        stmt = update(table).where(getattr(table, column) == expected_value).values(new_values)
        results = await session.execute(stmt)
        return results.rowcount

    async def select_indicators(self, table_columns: list, condition: list, session):
        items = select(*table_columns).where(*condition)

        results = await session.execute(items)

        return results

    async def post_item(self, item:Base, session: AsyncSession) -> Base:
        """Posts new item into given table"""
        session.add(item)
        await session.commit()

        return item

    async def delete_item(self, table: Base, column: str, value, session: AsyncSession):
        """Deletes item by criteria from given table"""

        stmt = delete(table).where(getattr(table, column) == value)
        results = await session.execute(stmt)
        deleted_rows_count = results.rowcount
        await session.commit()
        return deleted_rows_count

repo = Repository()
