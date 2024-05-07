from typing import List, Dict
from tables.data import DataDao
from utils.column import get_columns
from db import async_session


async def crate_data_for_graph(settlement_data: Dict, indicators_with_years: List[str]):

    indicators = list(set(column.split('_')[0] for column in indicators_with_years))

    indicators_years = {}
    indicators_data = {}
    for indicator in indicators:
        indicators_years[indicator] = []
        indicators_data[indicator] = []
    for column in indicators_with_years:
        indicator = column.split('_')[0]
        year = int(column.split('_')[1])
        value = settlement_data[column]
        indicators_years[indicator].append(year)
        indicators_data[indicator].append({
            'Year': year,
            indicator: value
        })
    return indicators_data, indicators_years


async def get_indicators_with_years() -> List[str]:
    indicators_with_years = []
    async with async_session() as session:
        columns = await get_columns(DataDao.__tablename__, session)
    column_names = list(columns.keys())[15:]
    for column in column_names:
        if column.find('_') != -1:
            indicators_with_years.append(column)
    return indicators_with_years
