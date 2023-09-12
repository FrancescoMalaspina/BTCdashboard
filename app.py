# Third party imports
import dash_bootstrap_components as dbc
import dash
from components import navbar

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.ZEPHYR], suppress_callback_exceptions=True)
nav = navbar.NavbarLogo()

app.layout = dbc.Container([
    nav,
    dash.page_container
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)