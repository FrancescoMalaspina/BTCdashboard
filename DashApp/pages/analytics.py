import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd

dash.register_page(__name__)
db_path = "database/BTC-USD.csv"


def layout(data=pd.read_csv(db_path)):
    return html.Div([
        html.H1('Analytics'),
        dcc.Dropdown(
            id='y-axis-scale',
            options=[
                {'label': 'Linear scale', 'value': 'linear'},
                {'label': 'Logarithmic scale', 'value': 'log'}
            ],
            value='linear',  # Default to linear scale
            clearable=False
        ),

        dcc.Graph(
            id='price-chart',
            config={'staticPlot': False},  # Allow updates to the graph
            figure=px.line(data, x='Date', y='Close', title='Bitcoin Price')
        ),
    ])


@callback(
    Output('price-chart', 'figure'),
    Input('y-axis-scale', 'value')
)
def update_y_axis_scale(scale, data=pd.read_csv(db_path)):
    if scale == 'log':
        yaxis_type = 'log'
    else:
        yaxis_type = 'linear'

    updated_figure = px.line(data, x='Date', y='Close', title='Bitcoin Price')
    updated_figure.update_yaxes(type=yaxis_type)

    return updated_figure
