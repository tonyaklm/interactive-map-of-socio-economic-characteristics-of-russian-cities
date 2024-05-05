from db import async_session
from common.repository import repo
from tables.data import DataDao
from graph.graph import Graph
import json
from fastapi import APIRouter
from subapp import graph_manager

router = APIRouter()


async def cache_graphs():
    selected_columns = ['settlement', 'longitude_dd', 'latitude_dd']
    indicators_with_years = []
    for column in DataDao.__table__.columns.keys()[15:]:
        if column.find('_') != -1:
            indicators_with_years.append(column)
    async with async_session() as session:
        selected_data = await repo.select_mean_indicator(DataDao, selected_columns,
                                                         indicators_with_years,
                                                         session)
        data = [row._asdict() for row in selected_data]

    for settlement_data in data:
        await cache_graph(settlement_data, indicators_with_years)


async def cache_graph(settlement_data: json, indicators_with_years):
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

    graph = Graph(settlement_data['settlement'], settlement_data['min_municipality_id'],
                  indicators_data, indicators_years)
    graph.create()
    graph.add_update_range_callback()
    graph.add_update_graph_callback()
    graph_manager.add_app(graph.get_path(), graph.get_app())
