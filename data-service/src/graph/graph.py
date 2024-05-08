from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
from typing import Dict, List


class Graph:
    def __init__(self, settlement: str, municipality: int, indicators_data: Dict[str, List[Dict]],
                 indicators_years: Dict[str, List[int]]):
        self.path: str = '/dashboard/{}/'.format(municipality)
        self.settlement: str = settlement
        self.app: Dash = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                              requests_pathname_prefix=self.path)
        self.indicators_data: Dict[str, List[Dict]] = indicators_data
        self.indicators_years: Dict[str, List[int]] = indicators_years
        self.indicators: List[str] = list(indicators_data.keys())

    # def create(self) -> None:
    #     self.app.layout = html.Div([
    #         html.H1(children='График индикаторов по городу {}'.format(self.settlement),
    #                 style={'text-align': 'center'}),
    #         html.Div([
    #             html.Div([
    #                 html.Label(['Выберите индикатор:'], style={'font-weight': 'bold'}),
    #                 dcc.Dropdown(
    #                     self.indicators,
    #                     self.indicators[0],
    #                     placeholder='Выберите индикатор',
    #                     id='dropdown',
    #                 )
    #             ],
    #                 style={'width': '49%', 'display': 'inline-block'}),
    #             html.Div(children='Выберите промежуток времени'),
    #             dcc.RangeSlider(min=min(self.indicators_years[self.indicators[0]]),
    #                             max=max(self.indicators_years[self.indicators[0]]),
    #                             marks={i: '{}'.format(i) for i in self.indicators_years[self.indicators[0]]}, step=1,
    #                             value=[min(self.indicators_years[self.indicators[0]]),
    #                                    max(self.indicators_years[self.indicators[0]])],
    #                             id='range'),
    #
    #             html.Div([
    #                 dcc.Graph(
    #                     id='crossfilter-indicator',
    #                     style={'margin-top': '20px'}
    #                 )
    #             ], style={'width': '80%', 'margin': '10 auto'})
    #         ])
    #
    #     ])

    def add_update_dropdown_callback(self) -> None:
        @self.app.callback(
            [Output('dropdown', 'options'),
             Output('dropdown', 'value')],
            [Input('dropdown', 'value'),
             Input('dropdown', 'options')]
        )
        def update_dropdown(indicator_chosen, dropdown_indicators):
            if not indicator_chosen:
                return self.indicators, indicator_chosen
            else:
                return dropdown_indicators, indicator_chosen

    def add_update_range_callback(self) -> None:
        @self.app.callback(
            [Output('range', 'marks'),
             Output('range', 'min'),
             Output('range', 'max'),
             Output('range', 'value')],
            [Input('dropdown', 'value')]
        )
        def update_range(indicator_chosen):
            if not indicator_chosen:
                return None, None, None, None
            min_value = min(self.indicators_years[indicator_chosen])
            max_value = max(self.indicators_years[indicator_chosen])
            range_value = [min(self.indicators_years[indicator_chosen]), max(self.indicators_years[indicator_chosen])]
            marks = {i: '{}'.format(i) for i in self.indicators_years[indicator_chosen]}
            return marks, min_value, max_value, range_value

    def add_update_graph_callback(self) -> None:
        @self.app.callback(
            Output('crossfilter-indicator', 'figure'),
            [Input('range', 'value'),
             Input('dropdown', 'value')]
        )
        def update_graph(range_chosen, indicator_chosen):
            if not indicator_chosen:
                return px.line()
            title_graph = 'Значение индикатора {} по городу {}'.format(indicator_chosen, self.settlement)

            dff = pd.DataFrame.from_records(self.indicators_data[indicator_chosen])

            fig = px.line(dff[(dff.Year >= range_chosen[0]) & (dff.Year <= range_chosen[1])].sort_values(['Year']),
                          x='Year',
                          y=indicator_chosen)
            fig.update_layout(title=title_graph,
                              xaxis_title='Год',
                              yaxis_title='Значение индикатора',
                              hovermode='x'
                              )

            return fig

    def create(self) -> None:
        self.app.layout = html.Div([
            html.H1(children='График индикаторов по городу {}'.format(self.settlement),
                    style={'text-align': 'center'}),
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

    def get_path(self) -> str:
        return self.path

    def get_app(self) -> Dash:
        return self.app

    def update_data(self, settlement: str, indicators_data: Dict[str, List[Dict]],
                    indicators_years: Dict[str, List[int]]) -> None:
        self.settlement = settlement
        self.indicators_data = indicators_data
        self.indicators_years = indicators_years
        self.indicators = list(indicators_data.keys())
