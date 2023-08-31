from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd

app = Dash(__name__)

data = pd.read_csv("database/BTC-USD.csv")
dashboard_table = data.head(10)

app.layout = html.Div([
    html.H1("Bitcoin Price Dashboard"),

    dcc.Graph(
        id='price-chart',
        figure=px.line(data, x='Date', y='Close', title='Bitcoin Price')
    ),

    dash_table.DataTable(
        id='price-table',
        columns=[{"name": col, "id": col} for col in dashboard_table.columns],
        data=dashboard_table.to_dict('records')
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)