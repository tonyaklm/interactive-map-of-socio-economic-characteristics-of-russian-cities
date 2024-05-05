from dash import Dash
from typing import Dict


class GraphManager:
    def __init__(self):
        self.graphs: Dict[str, Dash] = {}

    def add_app(self, path: str, dash_app: Dash) -> None:
        self.graphs[path] = dash_app

    def get_apps(self) -> Dict[str, Dash]:
        return self.graphs
