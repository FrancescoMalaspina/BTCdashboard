# Third party imports
import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# Local package imports
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
        variation = price - prev_price
        percentage_variation = variation / prev_price

    html_text = html.H4([
        f"{price:.2f} USD",
        html.Br(),  # add this line
        html.Span(
            f"{variation:.2f} ({percentage_variation:.4f}%)",
            style={
                "color": "red" if percentage_variation < 0 else "green",
                "font-size": "18px",
                "margin-left": "10px"
            }
        )
    ])
    return html_text


date_picker = dbc.InputGroup([
    dbc.InputGroupText("Select day"),
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=data.iloc[1]["Date"],
        max_date_allowed=data.iloc[-1]["Date"],
        initial_visible_month=data.iloc[-1]["Date"],
        date=data.iloc[-1]["Date"]
    )
])

col1 = dbc.Col([
    html.Br(),
    html.Br(),
    html.Br(),
    # html.H5("Spot price"),
    # html.Br(),
    dbc.Card([dbc.CardHeader("Spot price"),
              dbc.CardBody(spot_price(), id="BTC-price-card"),]),
    html.Br(),
    date_picker,
    html.Br(),
    html.H5("Graph options"),
    # html.Br(),
    dbc.InputGroup([
        dbc.InputGroupText("Scale"),
        dbc.Select(
            id='y-axis-scale',
            options=[{'label': 'Linear', 'value': 'linear'},
                     {'label': 'Logarithmic', 'value': 'log'}],
            value='linear',
        ),
    ]),
    html.Br(),
    dbc.InputGroup([
        dbc.Select(
            id='x-axis-range',
            options=[
                {'label': '1W', 'value': -7},
                {'label': '1M', 'value': -30},
                {'label': '6M', 'value': -180},
                {'label': 'YTD', 'value': 'YTD'},
                {'label': '1Y', 'value': -365},
                {'label': 'All time', 'value': 'Max'}],
            value=-30,
        ), dbc.InputGroupText("Range"),
    ]),
], width={"size": 3})

col2 = dbc.Col([
    html.Br(),
    html.H1("Historical price", style={"text-align": "right"}),
    dcc.Graph(
                id='candlestick-price-chart',
                config={'staticPlot': False},
                figure={}
    )
])

layout = dbc.Container([
    html.Br(),
    dbc.Row([
        col1,
        col2,
    ]),
], fluid=False)


@callback(
    Output("BTC-price-card", "children"),
    Input("my-date-picker-single", "date")
)
def update_card_body(day):
    return spot_price(data, day)


@callback(
    Output('candlestick-price-chart', 'figure'),
    [Input('y-axis-scale', 'value'),
     Input('x-axis-range', 'value'),
     Input("my-date-picker-single", "date")]
)
def update_figure(y_scale, x_range, selected_date):
    if y_scale == 'log':
        yaxis_type = 'log'
    else:
        yaxis_type = 'linear'

    if x_range == 'YTD':
        _data = data[data["Date"].dt.year == data.iloc[-1, 0].year]
    elif x_range == 'Max':
        _data = data
    else:
        x_range = int(x_range)
        _data = data[x_range:]

    updated_figure = go.Figure(data=[go.Candlestick(
        x=_data["Date"],
        open=_data["Open"],
        close=_data["Close"],
        high=_data["High"],
        low=_data["Low"]
    )])

    updated_figure.update_layout(
        xaxis_rangeslider_visible=False,
        title_text="Candlestick price chart",
        shapes=[dict(
            type="rect",
            yref="paper", y0=0, y1=0.1,
            xref="x", x0=selected_date, x1=selected_date,
            line=dict(color="blue", width=5)),
        ]
    )

    updated_figure.update_xaxes(title_text="date")
    updated_figure.update_yaxes(type=yaxis_type, title_text="price")

    return updated_figure
