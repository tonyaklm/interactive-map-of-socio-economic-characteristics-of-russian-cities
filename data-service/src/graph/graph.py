import asyncio

from dash import Dash, html, dcc, Input, Output, State
import pandas as pd
import plotly.express as px
from typing import Dict, List
from graph.utils_graph import get_indicators


class Graph:
    def __init__(self):
        self.path: str = '/dashboard/'
        self.app: Dash = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                              requests_pathname_prefix=self.path)

    def create(self) -> None:
        self.app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.H1(style={'text-align': 'center'}, id='title-graph'),
            html.Div([
                html.Div([
                    html.Label(['Выберите индикатор:'], style={'font-weight': 'bold'}),
                    dcc.Dropdown(
                        placeholder='Выберите индикатор',
                        id='dropdown',
                    )
                ],
                    style={'width': '49%', 'display': 'inline-block'}),
                html.Div(children='Выберите промежуток времени'),
                dcc.RangeSlider(step=1,
                                id='range'),

                html.Div([
                    dcc.Graph(
                        id='crossfilter-indicator',
                        style={'margin-top': '20px'}
                    )
                ], style={'width': '80%', 'margin': '10 auto'})
            ])

        ])

    def add_update_dropdown_callback(self) -> None:
        @self.app.callback(
            [Output('dropdown', 'options'),
             Output('dropdown', 'value')],
            [Input('dropdown', 'value'),
             Input('dropdown', 'options')]
        )
        def update_dropdown(indicator_chosen, dropdown_indicators):
            if not indicator_chosen:
                indicators = asyncio.run(get_indicators())
                return indicators, indicator_chosen
            else:
                return dropdown_indicators, indicator_chosen

    def add_update_title_callback(self) -> None:
        @self.app.callback(
            [Output('title-graph', 'children')],
            Input('url', 'search')
        )
        def update_graph(search):
            settlement = "somth"
            return ['График индикаторов по городу {}'.format(settlement)]

    # def add_update_range_callback(self) -> None:
    #     @self.app.callback(
    #         [Output('range', 'marks'),
    #          Output('range', 'min'),
    #          Output('range', 'max'),
    #          Output('range', 'value')],
    #         [Input('dropdown', 'value')],
    #         State('url', 'search')
    #     )
    #     def update_range(indicator_chosen, search):
    #         if not indicator_chosen:
    #             return None, None, None, None
    #         settlement = int(search.split('id=')[1])
    #         indicators_years = {}
    #         indicators_data = {}
    #         for indicator in indicators:
    #             years = []
    #             indicators_data[indicator] = []
    #             for column in data.columns:
    #                 if column.split('_')[0] == indicator:
    #                     year = int(column.split('_')[1])
    #                     value = df[df['id'] == settlement][column].values[0]
    #                     years.append(year)
    #                     indicators_data[indicator].append({
    #                         'Year': year,
    #                         indicator: value
    #                     })
    #             indicators_years[indicator] = years
    #         min_value = min(indicators_years[indicator_chosen])
    #         max_value = max(indicators_years[indicator_chosen])
    #         range_value = [min(indicators_years[indicator_chosen]), max(indicators_years[indicator_chosen])]
    #         marks = {i: '{}'.format(i) for i in indicators_years[indicator_chosen]}
    #         return marks, min_value, max_value, range_value
    #
    # def add_update_graph_callback(self) -> None:
    #     @self.app.callback(
    #         Output('crossfilter-indicator', 'figure'),
    #         [Input('range', 'value'),
    #          Input('dropdown', 'value')],
    #         State('url', 'search')
    #     )
    #     def update_graph(range_chosen, indicator_chosen, search):
    #         # print(search)
    #         if not indicator_chosen:
    #             return px.line()
    #         settlement = int(search.split('id=')[1])
    #         indicators_years = {}
    #         indicators_data = {}
    #         for indicator in indicators:
    #             years = []
    #             indicators_data[indicator] = []
    #             for column in data.columns:
    #                 if column.split('_')[0] == indicator:
    #                     year = int(column.split('_')[1])
    #                     value = df[df['id'] == settlement][column].values[0]
    #                     years.append(year)
    #                     indicators_data[indicator].append({
    #                         'Year': year,
    #                         indicator: value
    #                     })
    #             indicators_years[indicator] = years
    #         title_graph = 'Значение индикатора {} по городу {}'.format(indicator_chosen, settlement)
    #
    #         dff = pd.DataFrame.from_records(indicators_data[indicator_chosen])
    #
    #         fig = px.line(dff[(dff.Year >= range_chosen[0]) & (dff.Year <= range_chosen[1])].sort_values(['Year']),
    #                       x='Year',
    #                       y=indicator_chosen)
    #
    #         fig.update_layout(title=title_graph,
    #                           xaxis_title=f"{settlement}",
    #                           yaxis_title='Значение индикатора',
    #                           hovermode='x'
    #                           )
    #         return fig

    def get_path(self) -> str:
        return self.path

    def get_app(self) -> Dash:
        return self.app
