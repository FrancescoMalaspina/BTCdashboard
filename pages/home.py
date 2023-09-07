import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import date
from .data import BTCprice as data

dash.register_page(__name__, path='/')


def spot_price(data=data, day=None):
    if day is None:
        price = data.iloc[-1]["Close"]
        prev_price = data.iloc[-2]["Close"]
    elif data["Date"].isin([day]).any():
        data = data.set_index("Date")
        price = data.loc[day, "Close"]
        prev_price = data.shift(1).loc[day, "Close"]
    else:
        price = -1

    if price == -1:
        percentage_variation = 0
        variation = 0
    else:
        variation = price-prev_price
        percentage_variation = variation/prev_price

    html_text = html.H4([f"{price:.2f} USD",
        html.Span(
            f"{variation:.2f} ({percentage_variation:.4f}%)",
            style={
                "color": "red" if percentage_variation < 0 else "green",
                "font-size": "18px",
                "margin-left": "10px"})])
    return html_text


def layout():
    return dbc.Container([
        # html.Br(),
        # dbc.Row("Welcome to the homepage!"),
        html.Br(),
        dbc.Row([
            dbc.Col(dbc.Card(
                dbc.CardBody(spot_price(),
                             id="BTC-price-card", className="card-text"),
            ), className="w-33 mb-6", ),
            dbc.Col([
                dbc.Row([dbc.Col("Select day: ", align="right"),
                         dbc.Col(dcc.DatePickerSingle(
                             id='my-date-picker-single',
                             min_date_allowed=data.iloc[1]["Date"],
                             max_date_allowed=data.iloc[-1]["Date"],
                             initial_visible_month=data.iloc[-1]["Date"],
                             date=data.iloc[-1]["Date"]),),
                         ], align="center"),
            ]),
        ], align="center"),
        html.Br(),
        html.H2("Historical price"),
        html.Br(),
        dbc.Row(
            [
                dbc.Col("Select price scale:", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        id='y-axis-scale',
                        options=[{'label': 'Linear scale', 'value': 'linear'},
                                 {'label': 'Logarithmic scale', 'value': 'log'}],
                        value='linear',
                        clearable=False)),
                dbc.Col("Select period range:", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        id='x-axis-range',
                        options=[
                            {'label': '1W', 'value': -7},
                            {'label': '1M', 'value': -30},
                            {'label': '6M', 'value': -180},
                            {'label': 'YTD', 'value': 'YTD'},
                            {'label': '1Y', 'value': -365},
                            {'label': 'All time', 'value': 'Max'}],
                        value=-30))]),
        dcc.Graph(
            id='candlestick-price-chart',
            config={'staticPlot': False},
            figure={}),
    ],
        fluid=True)


@callback(
    Output('candlestick-price-chart', 'figure'),
    [Input('y-axis-scale', 'value'),
     Input('x-axis-range', 'value')]
)
def update_figure(y_scale, x_range):
    # data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
    if y_scale == 'log':
        yaxis_type = 'log'
    else:
        yaxis_type = 'linear'

    if x_range == 'YTD':
        _data = data[data["Date"].dt.year == data.iloc[-1, 0].year]
    elif x_range == 'Max':
        pass
    else:
        _data = data[x_range:]

    updated_figure = go.Figure(data=[go.Candlestick(
        x=_data["Date"],
        open=_data["Open"],
        close=_data["Close"],
        high=_data["High"],
        low=_data["Low"]
    )])
    updated_figure.update_layout(xaxis_rangeslider_visible=False, title_text="Candlestick price chart")
    updated_figure.update_xaxes(title_text="date")
    updated_figure.update_yaxes(type=yaxis_type, title_text="price")
    return updated_figure


@callback(
    Output("BTC-price-card", "children"),
    Input("my-date-picker-single", "date")
)
def update_card_body(day):
    return spot_price(data, day)

