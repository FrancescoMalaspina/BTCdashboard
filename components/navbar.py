# Third party imports
from dash import html, Input, Output, callback, State
import dash_bootstrap_components as dbc

pages = [
    dbc.NavItem(dbc.NavLink("Home", href="/")),
    dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
    dbc.NavItem(dbc.NavLink("Options", href="/options")),
]


def Navbar():
    layout = html.Div([
        dbc.NavbarSimple(
            children=pages,
            brand="BTC dashboard",
            brand_href="/",
            color="dark",
            dark=True,
        ),
    ])
    return layout


def NavbarLogo():
    layout = html.Div([
        dbc.Navbar(
            [
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src="/assets/BTClogo.png", height="45px", style={"margin-left": "0px"}), ),
                                dbc.Col(dbc.NavbarBrand("BTC dashboard", className="ml-2"), ),
                            ], align="center"),
                        dbc.Row(
                            [
                                dbc.Col(dbc.NavbarToggler(id="navbar-toggler", n_clicks=0), ),
                                dbc.Col(
                                    dbc.Collapse(
                                        dbc.Nav(pages, navbar=True, fill=True),
                                        id="navbar-collapse",
                                        is_open=False,
                                        navbar=True,
                                    ),
                                ),
                            ]
                        ),
                    ],
                ),
            ],
            color="dark",
            dark=True,
        ),
    ])
    return layout


# add callback for toggling the collapse on small screens
@callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
