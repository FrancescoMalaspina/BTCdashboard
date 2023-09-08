# Third party imports
from dash import html
import dash_bootstrap_components as dbc


def Navbar():
    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
                dbc.NavItem(dbc.NavLink("Options", href="/options")),
            ],
            brand="BTC dashboard",
            brand_href="/",
            color="dark",
            dark=True,
        ),
    ])
    return layout