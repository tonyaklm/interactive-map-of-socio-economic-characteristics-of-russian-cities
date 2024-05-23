from typing import Set, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from utils.check_columns import check_columns
from db import async_session
from common.map import FoliumMap
from utils.data import get_indicator_names, get_indicator, get_agg_func, get_target, select_regions


async def cache_maps():
    async with async_session() as session:
        await check_columns(session)

        regions = await select_regions(session)

        for indicator in await get_indicator_names(session):
            await cache_map(indicator, session, regions)

        folium_map = FoliumMap()
        await folium_map.create(regions, session)
        await folium_map.save()


async def cache_map(indicator: str, session: AsyncSession, regions: Optional[Set[int]] = None):
    folium_map = FoliumMap(indicator)
    if not regions:
        regions = await select_regions(session)
    await folium_map.create(regions, session)
    await folium_map.create_markers_layer()
    agg_func = await get_agg_func(indicator, session)
    data = await get_indicator(indicator, agg_func, session)
    min_value = await get_target(indicator, agg_func, 'min', session)
    max_value = await get_target(indicator, agg_func, 'max', session)
    await folium_map.add_colormap(min_value, max_value)
    for row in data:
        await folium_map.add_marker(row)
    await folium_map.save()


async def update_cache_map(indicators: List[str]):
    async with async_session() as session:
        await check_columns(session)
        regions = await select_regions(session)
        for indicator in indicators:
            await cache_map(indicator, session, regions)
