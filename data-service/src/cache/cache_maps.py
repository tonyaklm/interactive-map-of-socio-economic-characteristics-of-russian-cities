from sqlalchemy.ext.asyncio import AsyncSession
from utils.check_columns import check_columns
from db import async_session
from tables.data import DataDao
from common.map import FoliumMap
from routers.data import get_indicator

static_columns = ['population', 'children']


async def cache_maps():
    async with async_session() as session:
        await check_columns(session)

        for indicator in static_columns + DataDao.__table__.columns.keys()[15:]:
            await cache_map(indicator, session)
        FoliumMap().save()


async def cache_map(indicator: str, session: AsyncSession):
    folium_map = FoliumMap(indicator)
    data = await get_indicator(indicator, session)
    folium_map.add_colormap(data)
    for row in data:
        folium_map.add_marker(row)
    folium_map.save()
