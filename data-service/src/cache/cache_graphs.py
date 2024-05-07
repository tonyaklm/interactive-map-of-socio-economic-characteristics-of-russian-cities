from db import async_session
from common.repository import repo
from tables.data import DataDao
from graph.graph import Graph
import json
from subapp import graph_manager
from models import graph_data
from utils.graph_data import crate_data_for_graph, get_indicators_with_years


async def cache_graphs():
    selected_columns = ['settlement', 'longitude_dd', 'latitude_dd']
    indicators_with_years = await get_indicators_with_years()
    async with async_session() as session:
        selected_data = await repo.select_mean_indicator(DataDao, selected_columns,
                                                         indicators_with_years,
                                                         session)
    data = [row._asdict() for row in selected_data]

    for settlement_data in data:
        await cache_graph(settlement_data, indicators_with_years)


async def cache_graph(settlement_data: json, indicators_with_years):
    indicators_data, indicators_years = await crate_data_for_graph(settlement_data, indicators_with_years)

    graph = Graph(settlement_data['settlement'], settlement_data['min_municipality_id'],
                  indicators_data, indicators_years)
    graph.create()
    graph.add_update_range_callback()
    graph.add_update_dropdown_callback()
    graph.add_update_graph_callback()
    graph_manager.add_app(graph.get_path(), graph)


async def update_one_settlement(city_data: graph_data.UpdateGraphData):
    indicators_with_years = await get_indicators_with_years()
    async with async_session() as session:
        selected_data = await repo.select_settlement_indicators(DataDao, ['settlement'],
                                                                indicators_with_years,
                                                                ['settlement', 'longitude_dd', 'latitude_dd'],
                                                                [city_data.settlement, city_data.longitude_dd,
                                                                 city_data.latitude_dd],
                                                                session)
    settlement_data = [row._asdict() for row in selected_data][0]

    await update_graph(settlement_data, indicators_with_years)


async def update_all_settlements():
    selected_columns = ['settlement', 'longitude_dd', 'latitude_dd']
    indicators_with_years = await get_indicators_with_years()
    async with async_session() as session:
        selected_data = await repo.select_mean_indicator(DataDao, selected_columns,
                                                         indicators_with_years,
                                                         session)
    data = [row._asdict() for row in selected_data]

    for settlement_data in data:
        await update_graph(settlement_data, indicators_with_years)


async def update_graph(settlement_data, indicators_with_years):
    graph = graph_manager.get_app('/dashboard/{}/'.format(settlement_data['min_municipality_id']))

    indicators_data, indicators_years = await crate_data_for_graph(settlement_data, indicators_with_years)

    graph.update_data(settlement_data['settlement'], indicators_data, indicators_years)
