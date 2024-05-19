from common.repository import repo
from tables.data import DataDao
from tables.feature import FeatureDao

from db import async_session


async def get_indicators():
    async with async_session() as session:
        indicators = await repo.select_indicators(FeatureDao, "indicator_type", session)
        print(indicators)



# async def select_range_indicators(min_municipality_id: int):
#     async with async_session() as session:
#         city_data = await select_by_unique_column(DataDao, "id", min_municipality_id, session)


