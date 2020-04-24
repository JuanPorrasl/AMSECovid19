#####################################################################
#######     Dash Plotly with Bootstrap Components           #########
#####################################################################

#Loading datas
import logging
import os
import pathlib
import yaml

import dash
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State 

import plotly.graph_objects as go
import plotly.express as px

import urllib.request
import datetime
import time

from app import app, auth
from pages import page_france, page_brazil, page_worldwide, page_analysis


# Reading environment file for configuration
CONFIGURATION_FILE = 'environment.yaml'
CONFIGURATION_SECTION = os.environ.get('COVID_APP_ENV', 'local')

logging.info('Reading configuration file')
with open(CONFIGURATION_FILE, 'r') as file:
    config = yaml.safe_load(file)[CONFIGURATION_SECTION]

# Set up as before application directory
# TODO: to remove, because of no use if app correctly started
os.chdir(config['directory']['application'])


#Settings
# TODO: to remove, no usage in dash app, only in notebooks
pd.set_option('display.max_columns', 20)


#Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Worldwide", href="/")),
        dbc.NavItem(dbc.NavLink("Global analysis", href="/global")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Detailed studies", header=True),
                dbc.DropdownMenuItem("Brazil", href="/brazil"),
                dbc.DropdownMenuItem("France", href="/france"),
                dbc.DropdownMenuItem("United States", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="Countries",
        ),
    ],
    brand="Covid 19 Dashboard",
    brand_href="/",
    color="#384259",
    dark=True,
)
                
app.layout = (
        html.Div(children=[navbar,
                        dcc.Location(id="url", refresh=False), html.Div(id="page-content"),
                ],
                style={"background":"white", "margin-top:":"0"}
        )
)



# Update page
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/france":
        return page_france.create_layout(app)
    if pathname == "/brazil":
        return page_brazil.create_layout(app)
    if pathname == "/global":
        return page_analysis.create_layout(app)
    else:
        return page_worldwide.body_worldwide
  

if __name__ == '__main__':

    port = config.get('port', 8050)
    debug = config.get('debug', False)

    app.run_server(
        debug=debug,
	port=port,
    )

