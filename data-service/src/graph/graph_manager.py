from dash import Dash
from typing import Dict
from graph.graph import Graph


class GraphManager:
    def __init__(self):
        self.graphs: Dict[str, Graph] = {}

    def add_app(self, path: str, dash_app: Graph) -> None:
        self.graphs[path] = dash_app

    def get_apps(self) -> Dict[str, Graph]:
        return self.graphs

    def get_app(self, path) -> Graph:
        return self.graphs.get(path)
