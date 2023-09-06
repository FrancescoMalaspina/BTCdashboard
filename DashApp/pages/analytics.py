import dash
from dash import html, dcc, Input, Output, callback
import dash_latex as dl
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from .tools import log_return_chart, rolling_volatility_chart

dash.register_page(__name__)
db_path = "database/BTC-USD.csv"


def latex_text():
    text = [r'''
        Markdown explanation.
        Example equation:
        $$ 
        d S(t) = \mu S(t) dt + \sigma S(t) dW(t).
        $$''']
    return dl.DashLatex(text, displayMode=True)


def layout(data=pd.read_csv(db_path)):
    return dbc.Container([
        html.Br(),
        html.H1('Analytics'),
        html.Br(),
        dbc.Row([
            # dbc.Col(latex_text(), width=4),
            dbc.Col([
                dcc.Dropdown(
                    id='y-axis-scale',
                    options=[
                        {'label': 'Linear scale', 'value': 'linear'},
                        {'label': 'Logarithmic scale', 'value': 'log'}
                    ],
                    value='linear',  # Default to linear scale
                    clearable=False),
                dcc.Graph(
                    id='price-chart',
                    config={'staticPlot': False},  # Allow updates to the graph
                    figure=px.line(data, x='Date', y='Close', title='BTC Price')),
                dcc.Graph(
                    id='log-returns',
                    config={'staticPlot': False},
                    figure=log_return_chart(data)),
                html.H4("Historical Volatility"),
                dbc.Row([
                    dbc.Col("Select rolling window size [days]:", width="auto"),
                    dbc.Col(dcc.Input(
                        id='window-input',
                        type='number',
                        min=2,
                        value=200), )
                ]),
                dcc.Graph(
                    id='rolling-volatility',
                    config={'staticPlot': False},
                    figure=rolling_volatility_chart(data, window=200)),
                dbc.Row([
                    dbc.Col(),
                    dbc.Col()
                ])
            ]),
        ])
    ], fluid=True)


@callback(
    Output('price-chart', 'figure'),
    Input('y-axis-scale', 'value')
)
def update_y_axis_scale(scale, data=pd.read_csv(db_path)):
    if scale == 'log':
        yaxis_type = 'log'
    else:
        yaxis_type = 'linear'

    updated_figure = px.line(data, x='Date', y='Close', title='BTC Price')
    updated_figure.update_yaxes(type=yaxis_type)

    return updated_figure


@callback(
    Output('rolling-volatility', 'figure'),
    Input('window-input', 'value')
)
def update_graph(window, data=pd.read_csv(db_path)):
    return rolling_volatility_chart(data, window=int(window))
