#####################################################################
#######     Dash Plotly with Bootstrap Components           #########
#####################################################################
import os

import pandas as pd
import numpy as np
from datetime import datetime

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State 

from app import app
import plotly.graph_objects as go
import plotly.express as px

from cleaning_datas_docks import cargo, vessels, seacode, config

#Plot
years = vessels.groupby("date")[["counter"]].sum().fillna(0)[1:].index

vessels_number = go.Figure()
vessels_number.add_trace(go.Bar(x=years,
                y=vessels[vessels["cal_place_code"]=="FRFOS"].groupby("date")[["counter"]].sum().fillna(0)["counter"],
                name='FOS',
                visible=True,
                marker_color='rgb(55, 83, 109)'
                ))
vessels_number.add_trace(go.Bar(x=years,
                y=vessels[vessels["cal_place_code"]=="FRMRS"].groupby("date")[["counter"]].sum().fillna(0)["counter"],
                name='MRS',
                visible=True,
                marker_color='rgb(26, 118, 255)'
                ))
vessels_number.add_trace(go.Bar(x=years,
                y=vessels[vessels["cal_place_code"]=="FRFOS"].groupby("date")[["counter"]].sum().fillna(0).diff()[1:]["counter"],
                name='FOS',
                visible=False,
                marker_color='rgb(55, 83, 109)'
                ))
vessels_number.add_trace(go.Bar(x=years,
                y=vessels[vessels["cal_place_code"]=="FRMRS"].groupby("date")[["counter"]].sum().fillna(0).diff()[1:]["counter"],
                name='MRS',
                visible=False,
                marker_color='rgb(26, 118, 255)'
                ))

vessels_number.update_layout(
    title='Evolution of the number of ships by months in the port of Marseille/Fos',
    yaxis=dict(
        title='Number of vessels',
    ),

    barmode='group',
)
# Add range slider
vessels_number.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(count=5,
                     label="5y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        type="date"
    )
)

vessels_number.update_layout(
    updatemenus=[
        dict(
            type = "buttons",
            direction = "left",
            buttons=list([
                dict(
                    args=["barmode", "group"],
                    label="Groups",
                    method="relayout"
                ),
                dict(
                    args=["barmode", "stack"],
                    label="Stacks",
                    method="relayout"
                )
            ]),
            pad={"r": 0, "t": 0},
            showactive=True,
            x=1.2,
            xanchor="right",
            y=1,
            yanchor="bottom"
        ),
        dict(
            type="buttons",
            direction="left",
            pad={"r": 0, "t": 0},
            showactive=True,
            x=1.179,
            xanchor="right",
            y=1.10,
            yanchor="bottom",
            buttons=list([
                dict(label="None",
                     method="update",
                     args=[{"visible": [True, True, False, False]}]),
                dict(label="Diff",
                     method="update",
                     args=[{"visible": [False, False, True, True]}]),
            ]),
        ),
    ],
    
)

def create_layout(app):
    body = dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Title")
                        ],
                        xl=12,
                        
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
                                children=dcc.Graph(id='vessels_number', figure=vessels_number, config=config)
                            ),
                        ],
                        lg=12,
                    ),
                ],
                no_gutters=True,
            ),
        ],
        className="mt-4",
    )
                   
    return body




