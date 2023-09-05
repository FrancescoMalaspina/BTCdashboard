from dash import Dash, html, dcc
import dash
import pandas as pd

app = Dash(__name__, use_pages=True)

data = pd.read_csv("database/BTC-USD.csv")

app.layout = html.Div([
    html.H1("Bitcoin Multi-Page Price Dashboard"),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)