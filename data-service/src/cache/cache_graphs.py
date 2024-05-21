from graph.graph import Graph
from subapp import graph_manager


async def cache_graph():
    graph = Graph()
    graph.create()
    graph.add_update_title_callback()

    graph.add_update_range_callback()
    graph.add_update_dropdown_callback()
    graph.add_update_graph_callback()
    graph_manager.add_app(graph.get_path(), graph)

