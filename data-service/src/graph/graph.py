import asyncio

from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
from sqlalchemy.exc import ProgrammingError

from graph.utils_graph import get_indicators, get_settlement, get_years, get_indicators_data, get_region_data


class Graph:
    def __init__(self):
        self.path: str = "/dashboard/"
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
        def update_title(search):
            city_name = None
            if search.find('id=') != -1:
                min_mun_id = 0
                try:
                    min_mun_id = int(search.split('id=')[1])
                except IndexError:
                    city_name = None
                except ValueError:
                    city_name = None
                try:
                    city = asyncio.run(get_settlement(min_mun_id))
                except ProgrammingError:
                    city_name = None
                    city = None
                except IndexError:
                    city_name = None
                if city:
                    city_name = city.settlement

            return ['График индикаторов по городу {}'.format(city_name)]

    def add_update_range_callback(self) -> None:
        @self.app.callback(
            [Output('range', 'marks'),
             Output('range', 'min'),
             Output('range', 'max'),
             Output('range', 'value'),
             Output('range', 'step')],
            [Input('dropdown', 'value')]
        )
        def update_range(indicator_chosen):
            if not indicator_chosen:
                return None, None, None, None, 1
            try:
                indicators_years = asyncio.run(get_years(indicator_chosen))
            except ProgrammingError:
                return None, None, None, None, 1
            min_value = min(indicators_years)
            max_value = max(indicators_years)
            range_value = [min_value, max_value]
            marks = {i: '{}'.format(i) for i in indicators_years}
            return marks, min_value, max_value, range_value, None

    def add_update_graph_callback(self) -> None:
        @self.app.callback(
            Output('crossfilter-indicator', 'figure'),
            [Input('range', 'value'),
             Input('dropdown', 'value')],
            State('url', 'search')
        )
        def update_graph(range_chosen, indicator_chosen, search):
            none_value = px.line()
            if not indicator_chosen or search.find('id=') == -1:
                return none_value
            try:
                min_mun_id = int(search.split('id=')[1])
            except IndexError:
                return none_value
            except ValueError:
                return none_value
            try:
                city = asyncio.run(get_settlement(min_mun_id))
            except ProgrammingError:
                return none_value
            except IndexError:
                return none_value
            if not city:
                return none_value

            title_graph = 'Значение индикатора {} по городу {}'.format(indicator_chosen, city.settlement)
            indicators_years = asyncio.run(get_years(indicator_chosen))
            years = [year for year in indicators_years if range_chosen[0] <= year <= range_chosen[1]]
            try:
                settlement_data = asyncio.run(get_indicators_data(city, indicator_chosen, years))
                region_data = asyncio.run(get_region_data(city, indicator_chosen, years))
            except AttributeError:
                return none_value
            except ProgrammingError:
                return none_value

            fig = go.Figure()
            fig.add_scatter(x=years, y=list(settlement_data), name=f'Город: {city.settlement}', mode='markers+lines')
            fig.add_scatter(x=years, y=list(region_data), name=f'Регион: {city.region}', mode='markers+lines')

            fig.update_layout(title=title_graph,
                              xaxis_title=f"Год",
                              yaxis_title='Значение индикатора',
                              legend_title_text=f'Город или регион',
                              hovermode="x"
                              )
            fig.update_traces(hovertemplate=f'<b>{indicator_chosen}=%{{y}}</b><br><b>Year=%{{x}}</b>')
            return fig

    def get_path(self) -> str:
        return self.path[:-1]

    def get_app(self) -> Dash:
        return self.app
