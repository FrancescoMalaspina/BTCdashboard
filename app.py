from dash import Dash
import dash_bootstrap_components as dbc
import dash
import pandas as pd
from components import navbar

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
nav = navbar.Navbar()
data = pd.read_csv("database/BTC-USD.csv")

app.layout = dbc.Container([
    nav,
    # html.Div([html.Div(
    #         dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
    #     ) for page in dash.page_registry.values()]),
    dash.page_container
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)