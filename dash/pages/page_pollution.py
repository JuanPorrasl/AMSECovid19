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

import time
from datetime import datetime

def timer():
    return '['+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+']'

from cleaning_datas_pollution import df, safe_execute, fig_gauge, bar_color, CC, config

#Reverse color palets
px.colors.diverging.Spectral.reverse()

#Evolution of pollution for some countries
df_group=df.groupby(["cc_pays",df.date.dt.year,df.date.dt.month,df.date.dt.day], as_index=False).agg({'counter':'sum','calcul':'sum','date':'max'})
df_group["NO2"]=df_group.calcul/df_group.counter

#Convert cc_pays for ploting on a map
df_group["cc_name"]=[CC[elem] if elem != "Undefined" else "" for elem in df_group.cc_pays]
last_date=df_group.groupby("cc_pays").agg({"date":"max"}).to_dict()["date"]
df_group=df_group[df_group.date==[last_date[elem] for elem in df_group.cc_pays]]


map_NO2 = go.Figure(data=go.Choropleth(
    locations=df_group['cc_name'],
    z=df_group['NO2'],
    locationmode='country names',
    colorscale=px.colors.diverging.Spectral,
    autocolorscale=False,
    marker_line_color='#f2f2f2', # line markers between states
    colorbar_title="NO2"
))
map_NO2.update_geos(projection_type="natural earth",
                showocean=False,
                showframe=False,
                coastlinecolor="#f2f2f2",
)

map_NO2.update_layout(height=800,
                  title_text='Last NO2 concentration by countries',
                  margin={"r":0,"l":0,"b":0})




#Create badges last update
badges_updates=[dbc.Badge(str(elem)+": "+last_date[elem].strftime("%d/%m/%y"), style={'background':("#26de81" if ((last_date[elem]==df_group.date.max()) | (last_date[elem]==(df_group.date.max()-pd.Timedelta("1 days")))) else "#fed330")}, className="mr-1") for elem in df_group.cc_pays]

def create_layout(app):
    body = dbc.Container(
        [
            dbc.Container(
                #DROPDOWN MENU
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2("Economic indicators: air quality (NO2)"),
                            ],
                            xl=10,
                            
                        ),
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Latest Updates",
                                    id="collapse-updates-button",
                                    color="light",
                                    block=True,
                                    size="sm",
                                ),
                            ],
                            xl=2,
                            
                        ),
                    ],
                    justify="center",
                ),
                fluid=False,
                className="mb-2"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody(badges_updates)),
                                id="collapse_updates",
                            ),
                        ],
                        md=12,
                            
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
                                children=dcc.Graph(id='map-NO2', figure=map_NO2, config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
            ),
        ],
        className="mt-4",
        fluid=True,
    )
                   
    return body


@app.callback(
    Output("collapse_updates", "is_open"),
    [Input("collapse-updates-button", "n_clicks")],
    [State("collapse_updates", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open