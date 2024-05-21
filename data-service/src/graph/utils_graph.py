from typing import List

from common.repository import repo
from tables.data import DataDao
from tables.feature import FeatureDao

from db import async_session


async def get_indicators():
    async with async_session() as session:
        indicators = await repo.select_indicators([FeatureDao.indicator_type], [FeatureDao.is_drawable == True],
                                                  session)
        return indicators.scalars().all()


async def get_settlement(min_municipality_id: int):
    async with async_session() as session:
        settlement = await repo.select_by_unique_column(DataDao, "id", min_municipality_id, session)
        return settlement


async def get_years(indicator_type: str):
    async with async_session() as session:
        years = await repo.select_indicators([FeatureDao.years], [FeatureDao.indicator_type == indicator_type], session)
        return years.scalars().all()[0]


async def get_indicators_data(city: DataDao, indicator: str, years: List[int]):
    async with async_session() as session:
        indicators_with_years = [f"{indicator}_{year}" for year in years]
        data = await repo.select_settlement_indicators(DataDao,
                                                       indicators_with_years,
                                                       ['longitude_dd', 'latitude_dd'],
                                                       [city.longitude_dd,
                                                        city.latitude_dd],
                                                       session)
        return data[0]


async def get_region_data(city: DataDao, indicator: str, years: List[int]):
    async with async_session() as session:
        indicators_with_years = [f"{indicator}_{year}" for year in years]
        funcs = await repo.select_indicators([FeatureDao.agg_function], [FeatureDao.indicator_type == indicator],
                                             session)
        agg_func = funcs.scalars().all()[0]
        data = await repo.select_region_indicators(DataDao,
                                                   indicators_with_years,
                                                   ['longitude_dd', 'latitude_dd'],
                                                   "region_id",
                                                   city.region_id,
                                                   agg_func,
                                                   session)
        return data[0]
