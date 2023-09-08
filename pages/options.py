# Third party imports
import dash
from dash import html
import dash_bootstrap_components as dbc

# Local package imports
from .data import BTCprice as data

dash.register_page(__name__)


call = dbc.Card([
    dbc.CardHeader("Call"),
    dbc.CardBody(id="call-bs-price-card"),
])

col1 = dbc.Col([
    dbc.Label("Spot price"),
    dbc.InputGroup([
        dbc.InputGroupText("S"),
        dbc.Input(type="number", placeholder="0...")
    ]),
    dbc.Label("Strike price"),
    dbc.InputGroup([
        dbc.InputGroupText("X"),
        dbc.Input(type="number", placeholder="0...")
    ]),
    dbc.Label("Periods to maturity"),
    dbc.InputGroup([
        dbc.InputGroupText("T"),
        dbc.Input(type="number", min=0, step=1, placeholder="0...")
    ]),
    dbc.Label("Volatility"),
    dbc.InputGroup([
        dbc.InputGroupText("s"),
        dbc.Input(type="number", min=0, placeholder="0...")
    ]),
], width=4)

layout = dbc.Container([
    html.Br(),
    html.H1('Black & Scholes'),
    html.Br(),
    dbc.Row([
        col1,
        dbc.Col([]),
    ]),
])
