from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

app = Dash(__name__)

data = pd.read_csv("database/BTC-USD.csv")
dashboard_table = data.head(10)

app.layout = html.Div([
    html.H1("Bitcoin Price Dashboard"),

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
        id='candlestick-price-chart',
        config={'staticPlot': False},
        figure={}),

    dcc.Graph(
        id='price-chart',
        config={'staticPlot': False},  # Allow updates to the graph
        figure=px.line(data, x='Date', y='Close', title='Bitcoin Price')
    ),

    dash_table.DataTable(
        id='price-table',
        columns=[{"name": col, "id": col} for col in dashboard_table.columns],
        data=dashboard_table.to_dict('records')
    )
])

@app.callback(
    Output('price-chart', 'figure'),
    Input('y-axis-scale', 'value')
)
def update_y_axis_scale(scale):
    if scale == 'log':
        yaxis_type = 'log'
    else:
        yaxis_type = 'linear'

    updated_figure = px.line(data, x='Date', y='Close', title='Bitcoin Price')
    updated_figure.update_yaxes(type=yaxis_type)

    return updated_figure

@app.callback(
    Output('candlestick-price-chart', 'figure'),
    Input('y-axis-scale', 'value')
)
def update_y_axis_scale(scale):
    if scale == 'log':
        yaxis_type = 'log'
    else:
        yaxis_type = 'linear'

    updated_figure = figure=go.Figure(data=[go.Candlestick(
        x=data["Date"], 
        open=data["Open"], 
        close=data["Close"], 
        high=data["High"], 
        low=data["Low"])])
    updated_figure.update_layout(xaxis_rangeslider_visible=False).update_yaxes(type=yaxis_type)

    return updated_figure

if __name__ == '__main__':
    app.run_server(debug=True)