from sqlalchemy.ext.asyncio import AsyncSession
from utils.check_columns import check_columns
from db import async_session
from common.map import FoliumMap
from utils.data import get_indicator_names, get_indicator


async def cache_maps():
    async with async_session() as session:
        await check_columns(session)

        for indicator in await get_indicator_names(session):
            await cache_map(indicator, session)
            break
        FoliumMap().save()


async def cache_map(indicator: str, session: AsyncSession):
    folium_map = FoliumMap(indicator)
    data = await get_indicator(indicator, session)
    folium_map.add_colormap(data)
    for row in data:
        folium_map.add_marker(row)
    # folium_map.add_none_markers()
    folium_map.save()
