#####################################################################
#######     Dash Plotly with Bootstrap Components           #########
#####################################################################
import os

import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State 

from app import app

import plotly.graph_objects as go
import plotly.express as px

#Python Script
from cleaning_datas_US import config
#from cleaning_datas import df, today, yesterday, config

dropdown_options = [
        {'label':i, 'value': i} for i in range(1,10)
        ]

#Dropdown for countries tests
def create_layout(app):
    body = dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("US Analysis"),
                            html.P(["Latest Updates: ",dbc.Badge("SourceName: "+str("TBD"), color="danger", className="mr-1")])
                        ],
                        md=12,
                        
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col([
                        dcc.Dropdown(
                            id="selected_country",
                            options=dropdown_options,
                            value=1,
                            className="mb-2 mt-4",
                            clearable=False,
                        ),
                    ],
                    xl=4,
                    ),
                ],
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [              
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='graph-1', config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
                className="mb-2",
            ), 
        ],
        className="mt-4"
    )
                   
    return body


@app.callback(Output('graph-1', 'figure'),
              [Input('selected_country', 'value')])
def graph(selected_country):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[1,2,3,4],
        y=[1,selected_country,3,4]))
    fig.update_layout(height=400, title_text="Graph title")
    return fig
    
