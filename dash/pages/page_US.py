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
from cleaning_datas_US import config, df, df_state, US_results_states, first_day, last_day, counties
#from cleaning_datas import df, today, yesterday, config


#Dropdown for countries tests
def create_layout(app):
    body = dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("United States Analysis"),
                            html.P(["Latest Updates: ",dbc.Badge("USA Facts: "+str(last_day), color="danger", className="mr-1")])
                        ],
                        md=10,
                        
                    ),
                    dbc.Col(
                        [
                            dcc.DatePickerSingle(
                                id='days-slider',
                                min_date_allowed=first_day,
                                max_date_allowed=last_day,
                                initial_visible_month=last_day,
                                date=last_day,
                                display_format='D/M/Y',
                            ),
                        ],
                        md=2,
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
                                children=dcc.Graph(id='weekly-graph', config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
            ), 
            dbc.Row(
                [
                    dbc.Col(
                        [              
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='weekly-map', config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
            ), 
            dbc.Row(
                [
                    dbc.Col(
                        [              
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='total-cases-map', config=config)
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


@app.callback(Output('total-cases-map', 'figure'),
              [Input('days-slider', 'date')])
def graph(sel_date):
    fig = go.Figure(go.Choroplethmapbox(
        geojson=counties, 
        locations=df.countyFIPS, 
        z=df[sel_date],
        featureidkey="id",
        text=df["County Name"]+" ("+df.State+")",
        colorscale="Reds", 
        zmin=0, zmax=18,
        marker_line_width=0,
        hovertemplate = "<b>%{text}</b><br>Cases for 100 hbts: %{z}<extra></extra>",
    ))
    
    fig.update_layout(
        showlegend = False, 
        mapbox_style="carto-positron",
        mapbox_zoom=3, 
        mapbox_center = {"lat": 37.0902, "lon": -95.7129},
        height=700,
        margin={"r":0,"l":0,"b":0}, 
        title="Total cases for 100 habs per counties<br>"+pd.to_datetime(sel_date).strftime("%d %B %Y")
    )
    
    return fig
    
    
@app.callback(Output('weekly-map', 'figure'),
              [Input('days-slider', 'date')])
def graph(sel_date):
    temp=df_state.groupby("countyFIPS").sum().drop(columns=["stateFIPS"]).transpose()
    temp=100*(temp.diff().rolling(14, win_type='triang').mean()-temp.diff().shift(7).rolling(14, win_type='triang').mean())/temp.diff().shift(7).rolling(14, win_type='triang').mean()
    temp=temp.transpose().sort_values(last_day, ascending=True).transpose()
    
    ls_txt=[]
    for elem in temp.columns:
        try:
            ls_txt=ls_txt+[df.loc[df["countyFIPS"]==elem,"County Name"].values[0]]
        except:
            ls_txt=ls_txt+[""]
    
    
    fig = go.Figure(go.Choroplethmapbox(
        geojson=counties, 
        locations=temp.columns, 
        z=round(temp.loc[sel_date,:],2),
        featureidkey="id",
        colorscale=[[0.0, "rgb(49,54,149)"],
                    [0.5555555555555556, "rgb(224,243,248)"],
                    [1.0, "rgb(165,0,38)"]], 
        zmax=20,
        zmin=-20,
        text=ls_txt,
        marker_line_width=0,
        hovertemplate = "<b>%{text}</b><br>New cases over the last 7 days: %{z}%<extra></extra>",
    ))
    
    fig.update_layout(
        showlegend = False, 
        mapbox_style="carto-positron",
        mapbox_zoom=3, 
        mapbox_center = {"lat": 37.0902, "lon": -95.7129},
        height=700,
        margin={"r":0,"l":0,"b":0}, 
        title="Covid19 cases evolution over the last 7 days<br>"+pd.to_datetime(sel_date).strftime("%d %B %Y")
    )
    return fig



@app.callback(Output('weekly-graph', 'figure'),
              [Input('days-slider', 'date')])
def graph(sel_date):
    temp=df_state[df_state.columns[2:]].groupby("State").sum().drop(columns=["stateFIPS"]).transpose()
    temp=100*(temp.diff().rolling(14, win_type='triang').mean()-temp.diff().shift(7).rolling(14, win_type='triang').mean())/temp.diff().shift(7).rolling(14, win_type='triang').mean()
    temp=temp.transpose().sort_values(sel_date, ascending=True).transpose()
    
    last_day_7=(pd.to_datetime(sel_date, format="%Y-%m-%d")-pd.Timedelta("7 days")).strftime("%Y-%m-%d")
    last_day_14=(pd.to_datetime(sel_date, format="%Y-%m-%d")-pd.Timedelta("14 days")).strftime("%Y-%m-%d")
    
    colors_plot=[]
    
    for elem in temp.columns:
        if US_results_states.loc[(US_results_states.State==elem),"trump"].values[0]:
            colors_plot=colors_plot+["#e13030"]
        else:
            colors_plot=colors_plot+["#00aeef"]
    

    fig = go.Figure()
    
    
    fig.add_trace(go.Scatter(
            x=temp.loc[last_day_14,:],
            y=temp.columns,
            marker=dict(color=["rgba(144,144,144,0.4)"]*temp.shape[1], size=4),
            mode="markers",
            name="14 days ago",
    ))
    
    
    fig.add_trace(go.Scatter(
            x=temp.loc[last_day_7,:],
            y=temp.columns,
            marker=dict(color=["rgba(144,144,144,0.8)"]*temp.shape[1], size=6),
            mode="markers",
            name="7 days ago",
    ))
    
    fig.add_trace(go.Scatter(
            x=temp.loc[sel_date,:],
            y=temp.columns,
            marker=dict(color=colors_plot, size=8),
            mode="markers",
            name="Today - Red for<br>republicans",
    ))
    
    
    fig.update_layout(title="Weekly covid19 evolution over the last 7 days by State<br>"+pd.to_datetime(sel_date).strftime("%d %B %Y")+", <i>Colored by elections results 2020</i>",
                      xaxis_title="Weekly covid19 evolution over the last 7 days (in %)",
                      height=1000,
                      yaxis_title="States")
    
    return fig
