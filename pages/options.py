# Third party imports
import dash
from dash import html
import dash_bootstrap_components as dbc

# Local package imports
from .data import BTCprice as data

dash.register_page(__name__)

layout = dbc.Container([
    html.Br(),
    html.H1('Black & Scholes'),
    html.Br(),
    dbc.Row([
        dbc.Col([], width=4),
        dbc.Col([]),
    ]),
])
