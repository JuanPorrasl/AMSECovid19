#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 16:26:14 2020

@author: juanporras
"""

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

from cleaning_datas import df, last_file_hopkins, config, df_pop
from cleaning_datas_tests import OWData

############# PLOT PART #############
#Dropdown for neighbourhood
dropdown_options = [
        {'label':i, 'value': i} for i in OWData['location'].unique()
        ]

def create_layout(app):
    body = dbc.Container(
        [
            #Dropdown
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Tests Performed Worldwide"),
                        ],
                        md=12,
                        
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [              
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='test_line',figure=test_line, config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
                className="mb-2",
            ),  
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Tests / Confirmed / Deaths"),
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
                            value='Worldwide',
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
                                children=dcc.Graph(id='Covid19-tests', config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
            ),
        ],
        className="mt-4"
    )
                   
    return body

#Covid19 tests
    
test_line = px.line(OWData, y='total_tests', x="date", color="location")
test_line.update_layout(title='Covid19 tests',
                   xaxis_title='',
                   yaxis_title='')

@app.callback(Output('Covid19-tests', 'figure'),
              [Input('selected_country', 'value')])
def update_cumulative_cases(selected_country):
    
    cond = (OWData['location']==selected_country)
    OWD = OWData[cond]
    
    fig = go.Figure()
    
    #Confirmed
    fig.add_trace(go.Scatter(
        x=OWD["date"],
        y=OWD['total_tests'],
        name='Total tests',
        #connectgaps=True,
    ))
    fig.add_trace(go.Scatter(
        x=OWD["date"],
        y=OWD["total_cases"],
        name='Confirmed Cases',
        #connectgaps=True,
    ))
    fig.add_trace(go.Scatter(
        x=OWD["date"],
        y=OWD["total_deaths"],
        name='Deaths',
        #connectgaps=True,
    ))

    fig.update_layout(xaxis_rangeslider_visible=True)

    return fig


