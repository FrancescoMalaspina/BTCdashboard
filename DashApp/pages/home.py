import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path='/')
db_path = "database/BTC-USD.csv"


def layout(data=pd.read_csv(db_path)):
    return html.Div([
        html.H1('Homepage'),
        dcc.Dropdown(
            id='y-axis-scale',
            options=[
                {'label': 'Linear scale', 'value': 'linear'},
                {'label': 'Logarithmic scale', 'value': 'log'}],
            value='linear',  # Default to linear scale
            clearable=False),
        dcc.RadioItems(
            id='x-axis-range',
            options=['1W', '1M', '6M', 'YTD', '1Y', '5Y', 'Max'],
            value='1W'
        ),
        dcc.Graph(
            id='candlestick-price-chart',
            config={'staticPlot': False},
            figure={}),
        dash_table.DataTable(
            id='price-table',
            columns=[{"name": col, "id": col} for col in data.columns],
            data=data.head(10).to_dict('records')
        )
    ])


@callback(
    Output('candlestick-price-chart', 'figure'),
    Input('y-axis-scale', 'value')
)
def update_y_axis_scale(scale, data=pd.read_csv(db_path)):
    if scale == 'log':
        yaxis_type = 'log'
    else:
        yaxis_type = 'linear'

    updated_figure = figure = go.Figure(data=[go.Candlestick(
        x=data["Date"],
        open=data["Open"],
        close=data["Close"],
        high=data["High"],
        low=data["Low"])])
    updated_figure.update_layout(xaxis_rangeslider_visible=False).update_yaxes(type=yaxis_type)

    return updated_figure
