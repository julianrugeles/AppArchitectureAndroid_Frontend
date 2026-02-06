from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

aapp = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server
