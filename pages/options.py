# Third party imports
import dash
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc

# Local package imports
# from .data import BTCprice as data
from components.option_pricing.black_scholes import BlackScholesModel, OptionType
from .tools import call_spot_curve

dash.register_page(__name__)

call = dbc.Card([
    dbc.CardHeader("Call"),
    dbc.CardBody(id="call-price-card"),
])

col1 = dbc.Col([
    dbc.Label("Spot price"),
    dbc.InputGroup([
        dbc.InputGroupText("S"),
        dbc.Input(type="number", min=1, value=25000, id="input-S")
    ]),
    dbc.Label("Strike price"),
    dbc.InputGroup([
        dbc.InputGroupText("X"),
        dbc.Input(type="number", min=1, value=25000, id="input-X")
    ]),
    dbc.Label("Periods to maturity"),
    dbc.InputGroup([
        dbc.InputGroupText("T"),
        dbc.Input(type="number", min=1, step=1, value=30, id="input-T")
    ]),
    dbc.Label("Risk free interest rate"),
    dbc.InputGroup([
        dbc.InputGroupText("r"),
        dbc.Input(type="number", min=1e-12, value=0.001, id="input-r")
    ]),
    dbc.Label("Volatility"),
    dbc.InputGroup([
        dbc.InputGroupText("v"),
        dbc.Input(type="number", min=1e-6, value=1, id="input-v")
    ]),
    html.Br(),
    call,
], width=4)

col2 = dbc.Col([dcc.Graph(figure={}, id='call-spot-curve')])

layout = dbc.Container([
    html.Br(),
    html.H1('Black & Scholes'),
    html.Br(),
    dbc.Row([
        col1,
        col2,
    ]),
])

@callback(
    Output('call-price-card', 'children'),
    [Input('input-S', 'value'),
     Input('input-X', 'value'),
     Input('input-r', 'value'),
     Input("input-T", "value"),
     Input("input-v", "value")]
)
def update_call_price(S, X, T, r, v):
    optionModel = BlackScholesModel(S, X, T, r, v)
    return optionModel.option_price(OptionType.CALL_OPTION)


@callback(
    Output('call-spot-curve', 'figure'),
    [
     Input('input-X', 'value'),
     Input('input-r', 'value'),
     Input("input-T", "value"),
     Input("input-v", "value")]
)
def update_call_price(X, T, r, v):
    return call_spot_curve(X, T, r, v)


