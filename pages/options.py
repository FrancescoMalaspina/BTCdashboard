# Third party imports
import dash
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
import numpy as np

# Local package imports
# from .data import BTCprice as data
from components.option_pricing.black_scholes import BlackScholesModel, OptionType
from components.tools import call_spot_curve, delta_hedging_curve

dash.register_page(__name__)

call = dbc.Card([
    dbc.CardHeader("Call price"),
    dbc.CardBody(id="call-price-card"),
])

put = dbc.Card([
    dbc.CardHeader("Put price"),
    dbc.CardBody(id="put-price-card"),
])

delta = dbc.Card([
    dbc.CardHeader("Delta hedging"),
    dbc.CardBody(id="delta-hedging-card"),
])

col1 = dbc.Col([
    html.Br(),
    html.H1('Black & Scholes'),
    html.Br(),
    dbc.Label("Spot price"),
    dcc.Slider(
        id="input-S",
        min=1,
        max=40000,
        step=1,
        value=20000,
        marks={i: str(i) for i in range(0, 40001, 10000)}
    ),
    dbc.Label("Strike price"),
    dcc.Slider(
        id="input-X",
        min=1,
        max=50000,
        step=1,
        value=25000,
        marks={i: str(i) for i in range(0, 50001, 10000)}
    ),
    dbc.Label("Periods to maturity"),
    dcc.Slider(
        id="input-T",
        min=1,
        max=365,
        step=1,
        value=180,
        marks={i: str(i) for i in range(0, 366, 30)}
    ),
    dbc.Label("Risk free interest rate"),
    dcc.Slider(
        id="input-r",
        min=1e-3,
        max=0.1,
        step=1e-3,
        value=5e-2,
        marks={i: f"{i * 100:.0f}%" for i in np.linspace(0, 0.1, 11)}
    ),
    dbc.Label("Volatility"),
    dcc.Slider(
        id="input-v",
        min=1e-2,
        max=1.5,
        step=1e-2,
        value=0.75,
        marks={i: f"{i * 100:.0f}%" for i in np.linspace(0, 1.5, 11)}
    ),
    html.Br(),
    html.Br(),
    call,
    html.Br(),
    # put,
    html.Br(),
    delta,
], width=4, align="stretch")

col2 = dbc.Col(
    [
        dcc.Graph(figure={}, id='call-spot-curve'),
        dcc.Graph(figure={}, id='delta-hedging-curve')
    ]
)

layout = dbc.Container([
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
     Input('input-T', 'value'),
     Input("input-r", "value"),
     Input("input-v", "value")]
)
def update_call_price(S, X, T, r, v):
    call_price = BlackScholesModel(S, X, T, r, v).option_price(OptionType.CALL_OPTION)
    return html.H5(f"{call_price:.2f}")


@callback(
    Output('delta-hedging-card', 'children'),
    [Input('input-S', 'value'),
     Input('input-X', 'value'),
     Input('input-T', 'value'),
     Input("input-r", "value"),
     Input("input-v", "value")]
)
def update_delta_hedging(S, X, T, r, v):
    delta_hedging = BlackScholesModel(S, X, T, r, v).delta_hedging(OptionType.CALL_OPTION)
    return html.H5(f"{delta_hedging:.2f}")


@callback(
    Output('call-spot-curve', 'figure'),
    [
        Input('input-S', 'value'),
        Input('input-X', 'value'),
        Input('input-T', 'value'),
        Input("input-r", "value"),
        Input("input-v", "value")]
)
def update_call_price_curve(S, X, T, r, v):
    return call_spot_curve(S, X, T, r, v)


@callback(
    Output('delta-hedging-curve', 'figure'),
    [
        Input('input-S', 'value'),
        Input('input-X', 'value'),
        Input('input-T', 'value'),
        Input("input-r", "value"),
        Input("input-v", "value")]
)
def update_delta_hedging_curve(S, X, T, r, v):
    return delta_hedging_curve(S, X, T, r, v)
