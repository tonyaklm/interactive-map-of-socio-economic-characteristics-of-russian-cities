from common.repository import repo
from tables.feature import FeatureDao
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession


async def get_indicator_types(session: AsyncSession) -> List[str]:
    indicator_types = await repo.select_indicators([FeatureDao.indicator_type], [],
                                                   session)

    return indicator_types.scalars().all() + ["Empty_Map"]


async def get_descriptions(session: AsyncSession) -> Dict[str, str]:
    descriptions = await repo.select_indicators([FeatureDao.indicator_type, FeatureDao.description], [],
                                                session)

    description_types = {}
    for element in [row._asdict() for row in descriptions.all()]:
        description_types[element['indicator_type']] = "{}: {}".format(element['indicator_type'], element['description'])
    description_types["Empty_Map"] = "Пустая карта"
    return description_types


async def get_drawable_columns(session: AsyncSession) -> List[str]:
    drawable_columns = await repo.select_indicators([FeatureDao.indicator_type], [FeatureDao.is_drawable == True],
                                                    session)
    return drawable_columns.scalars().all()


async def get_drawable_values(session: AsyncSession) -> Dict[str, List]:
    values = await repo.select_indicators([FeatureDao.years, FeatureDao.indicator_type],
                                          [FeatureDao.is_drawable == True], session)
    drawable_values = {}
    for element in [row._asdict() for row in values.all()]:
        drawable_values[element['indicator_type']] = sorted(element['years'])
    return drawable_values
