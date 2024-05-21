from typing import Optional

from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession
from common.repository import repo
from tables.feature import FeatureDao
from graph.utils_graph import get_years


async def post_new_feature(indicator: str, session: AsyncSession, description: Optional[str] = None,
                           agg_func: Optional[str] = None) -> None:
    indicator_type = indicator.split('_')[0] if indicator.find('_') != -1 else indicator
    try:
        new_feature = FeatureDao(
            indicator_type=indicator_type,
            is_drawable=True if indicator.find('_') != -1 else False,
            years=[int(indicator.split('_')[1])] if indicator.find('_') != -1 else [],
            description=description,
            agg_function=agg_func,
        )
        await repo.post_item(new_feature, session)
        return
    except IntegrityError:
        await session.rollback()
    years = await get_years(indicator_type)
    await repo.update_by_unique_column(FeatureDao, "indicator_type", indicator_type, {
        "years": years + [int(indicator.split('_')[1])] if indicator.find('_') != -1 else []
    }, session)
    await session.commit()


async def delete_feature(indicator: str, session: AsyncSession) -> None:
    indicator_type = indicator.split('_')[0] if indicator.find('_') != -1 else indicator
    year = int(indicator.split('_')[1]) if indicator.find('_') != -1 else None
    years = await get_years(indicator_type)
    if not years:
        await repo.delete_item(FeatureDao, "indicator_type", indicator_type, session)
        return
    elif years == [year]:
        await repo.delete_item(FeatureDao, "indicator_type", indicator_type, session)
        return
    else:
        try:
            years.remove(year)
        except ValueError:
            pass
        await repo.update_by_unique_column(FeatureDao, "indicator_type", indicator_type, {
            "years": years
        }, session)
        await session.commit()


async def update_feature_description(indicator_type: str, new_description: str, session: AsyncSession) -> int:
    updated_rows = await repo.update_by_unique_column(FeatureDao, "indicator_type", indicator_type, {
        "description": new_description
    }, session)
    await session.commit()
    return updated_rows
