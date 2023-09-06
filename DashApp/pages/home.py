import dash
from dash import html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path='/')
db_path = "database/BTC-USD.csv"


def layout(data=pd.read_csv(db_path)):
    return dbc.Container([
        html.Br(),
        dbc.Row("Welcome to the homepage!"),
        html.Br(),
        html.H2("Historical price"),
        html.Br(),
        dbc.Row(
            [
                dbc.Col("Select y-axis scale:", width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        id='y-axis-scale',
                        options=[{'label': 'Linear scale', 'value': 'linear'},
                                 {'label': 'Logarithmic scale', 'value': 'log'}],
                        value='linear',
                        clearable=False)),
                dbc.Col("Select x-axis range:", width="auto"),
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
        dbc.Table(dash_table.DataTable(
            id='price-table',
            columns=[{"name": col, "id": col} for col in data.columns],
            data=data.tail(10).to_dict('records')
        ), bordered=True)],
        fluid=True)


@callback(
    Output('candlestick-price-chart', 'figure'),
    [Input('y-axis-scale', 'value'),
     Input('x-axis-range', 'value')]
)
def update_figure(y_scale, x_range, data=pd.read_csv(db_path)):
    data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
    if y_scale == 'log':
        yaxis_type = 'log'
    else:
        yaxis_type = 'linear'

    if x_range == 'YTD':
        data = data[data["Date"].dt.year == data.iloc[-1, 0].year]
    elif x_range == 'Max':
        pass
    else:
        data = data[x_range:]

    updated_figure = go.Figure(data=[go.Candlestick(
        x=data["Date"],
        open=data["Open"],
        close=data["Close"],
        high=data["High"],
        low=data["Low"]
    )])
    updated_figure.update_layout(xaxis_rangeslider_visible=False, title_text="Candlestick price chart")
    updated_figure.update_xaxes(title_text="date")
    updated_figure.update_yaxes(type=yaxis_type, title_text="price")
    return updated_figure
