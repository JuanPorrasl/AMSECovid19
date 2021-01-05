import os

import dash
import dash_bootstrap_components as dbc
import dash_auth
#import sys


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Covid19 - AMSE Student Dashboard'
server = app.server
app.config.suppress_callback_exceptions = True

