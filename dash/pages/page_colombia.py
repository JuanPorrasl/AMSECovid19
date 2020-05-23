#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 14:03:42 2020

@author: juanporras
"""


#####################################################################
#######     Dash Plotly with Bootstrap Components           #########
#####################################################################
import os

import pandas as pd
import numpy as np
from astropy.convolution import convolve, Gaussian1DKernel
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State 

from app import app

import plotly.graph_objects as go
import plotly.express as px

#Python Script
from cleaning_datas_co import COL_Covid, COL_City_Covid, COL_Dep_Covid, states_co
from cleaning_datas_co import Covid_BOG, Localidad_Map,local_bog
from cleaning_datas import df, today, yesterday, config

#Cases by department
Covid_state_dep = pd.DataFrame(COL_Covid.groupby(['Department','State_of_treatment'])['Cases'].agg('sum')).reset_index()
Covid_state_dep.sort_values(by=['Cases','Department'],ascending=False,inplace=True)

bar_dep = px.bar(Covid_state_dep, x="Department", y="Cases", color='State_of_treatment',
                    color_discrete_sequence=['steelblue','palegreen','orangered','gray','darkred'])
bar_dep.update_layout(title_text="Confirmed cases by department")

#Cases by cities
Covid_state_city = pd.DataFrame(COL_Covid.groupby(['City','State_of_treatment'])['Cases'].agg('sum')).reset_index().sort_values(by='Cases',ascending=False)
Covid_state_city.sort_values(by=['Cases','City'],ascending=False)

bar_city = px.bar(Covid_state_city, x="City", y="Cases", color='State_of_treatment',
                  color_discrete_sequence=['steelblue','palegreen','orangered','gray','darkred'])
bar_city.update_layout(title_text="Confirmed cases by city", xaxis_rangeslider_visible=True)
#bar_city.update_layout(height=400, margin={"r":0,"t":0,"l":0,"b":0})

#Pie charts
#State_of_treatment
State = pd.DataFrame(COL_Covid.groupby(['State_of_treatment'])['Cases'].sum()).reset_index()
pie_state = px.pie(State, values=State['Cases'], names=State['State_of_treatment'], hole=.7,
            color_discrete_sequence=['steelblue','palegreen','orangered','gray','darkred'])
pie_state.update_layout(title_text="Health Condition")

#Sex
Sex = pd.DataFrame(COL_Covid.groupby(['Sex'])['Cases'].sum()).reset_index()
pie_sex = px.pie(Sex, values=Sex['Cases'], names=Sex['Sex'], hole=.7,
            color_discrete_sequence=['lightskyblue','lightgreen'])
pie_sex.update_layout(title_text="Sex")

SexState = pd.DataFrame(COL_Covid.groupby(['Sex','State_of_treatment'])['Cases'].sum()).reset_index()

#Correcting values of departments ONLY for the map
COL_MAP = COL_Dep_Covid
COL_MAP['Department_DANE'] = COL_MAP['Department_DANE'].replace({'NARINO':'NARIÑO'})

states_co["features"][2]["id"] = states_co["features"][2]["id"].replace('SANTAFE DE BOGOTA D.C','BOGOTA, D. C.')
states_co["features"][32]["id"] = states_co["features"][32]["id"].replace('ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA','ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA')
#Map info
COL_MAP['text'] = 'Department: ' + COL_MAP['Department_DANE'].astype(str) + '<br>' + \
    'Active: ' + COL_MAP['Active'].astype(str) + '<br>' + \
    'Deaths: ' + COL_MAP['Death'].astype(str) + '<br>' + \
    'Recovered: ' + COL_MAP['Recovered'].astype(str) + '<br>' + \
    'Hospitalization: ' + COL_MAP['Hospitalization'].astype(str) + '<br>' + \
    'Intensive Care: ' + COL_MAP['Intensive Care'].astype(str)

### BOGOTÁ CITY ###
    
Covid_estado = pd.DataFrame(Covid_BOG.groupby(['District','State of treatment'])['Cases'].agg('sum')).reset_index()
Covid_estado = Covid_estado.sort_values(by='Cases', ascending=False, inplace=False)

bar_bog = px.bar(Covid_estado, x="District", y="Cases", color='State of treatment',
            color_discrete_sequence=['steelblue','palegreen','orangered','gray','darkred'])
bar_bog.update_layout(title_text="Bogotá confirmed cases by district")

Localidad_Map['text'] = 'District: ' + Localidad_Map['District'].astype(str) + '<br>' + \
    'Active: ' + Localidad_Map['Active'].astype(str) + '<br>' + \
    'Deaths: ' + Localidad_Map['Death'].astype(str) + '<br>' + \
    'Recovered: ' + Localidad_Map['Recovered'].astype(str) + '<br>' + \
    'Hospitalization: ' + Localidad_Map['Hospital'].astype(str) + '<br>' + \
    'Intensive Care: ' + Localidad_Map['Intensive Care'].astype(str)

Localidad_Map['text_recover'] = 'District: ' + Localidad_Map['District'].astype(str) + '<br>' + \
    'Home: ' + Localidad_Map['Home'].astype(str) + '<br>' + \
    'Recovered: ' + Localidad_Map['Recovered'].astype(str) + '<br>' + \
    'Recovery Rate: ' + Localidad_Map['Recovery Rate'].astype(str) + '<br>' + \
    'Fatality Rate: ' + Localidad_Map['Fatality Rate'].astype(str)

#Pie charts
#State_of_treatment

State_bog = pd.DataFrame(Covid_BOG.groupby(['State of treatment'])['Cases'].sum()).reset_index()
pie_bog_state = px.pie(State, values=State_bog['Cases'], names=State_bog['State of treatment'], hole=.7,
            color_discrete_sequence=['steelblue','palegreen','orangered','gray','darkred'])
pie_bog_state.update_layout(title_text="Health Condition")
#Sex
Sex_bog = pd.DataFrame(Covid_BOG.groupby(['Sex'])['Cases'].sum()).reset_index()
pie_bog_sex = px.pie(Sex_bog, values=Sex_bog['Cases'], names=Sex_bog['Sex'], hole=.7,
            color_discrete_sequence=['lightskyblue','lightgreen'])
pie_bog_sex.update_layout(title_text="Sex")

def create_layout(app):
    body = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Colombia Covid19 evolution")
                        ],
                        md=12,
                        
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            #html.H5("Confirmed cases by department"),
                            
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='col-map',figure=col_map, config=config)
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
                            #html.H5("Confirmed cases by city"),
                        dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='city_cases',figure=bar_dep, config=config)
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
                            #html.H5("State of health"),
                        dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='health_state',figure=pie_state, config=config)
                            ),                       
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            #html.H5("Cases by sex"),
                        dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='sex_cases',figure=pie_sex, config=config)
                            ),                       
                        ],
                        md=6,
                    ),
                ],
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Bogotá Covid19 evolution")
                        ],
                        md=12,
                        
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            #html.H5("Confirmed cases by department"),
                            
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='bog-map',figure=bog_map, config=config)
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
                        dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='bog_health_state',figure=bar_bog, config=config)
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
                            #html.H5("State of health"),
                        dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='health_state',figure=pie_bog_state, config=config)
                            ),                       
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            #html.H5("Cases by sex"),
                        dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='sex_cases',figure=pie_bog_sex, config=config)
                            ),                       
                        ],
                        md=6,
                    ),
                ],
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Bogotá Recovery")
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
                                children=dcc.Graph(id='recovery-map',figure=recovery_map, config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
                className="mb-2",
            ),
        ],
        className="mt-4",
    )
                   
    return body

#Colombia COVID19 map

col_map = go.Figure(go.Choroplethmapbox(geojson=states_co, locations=COL_MAP['Department_DANE'],
                                    z=COL_MAP['Total'],
                                    text=COL_MAP['text'],
                                    colorscale='matter', zmin=0,
                                    colorbar_title = "Confirmed Cases",
                                    marker_opacity=0.5, marker_line_width=0.2))
col_map.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=4.50, mapbox_center = {"lat": 4.795100212097175, "lon": -74.022903442382812})
col_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


# Cases by city table

COL_City_Covid = COL_City_Covid.sort_values(by='Active',ascending=False)
COL_City_Covid.style.background_gradient(cmap='Reds',subset=["Intensive Care"])\
                        .background_gradient(cmap='Greys',subset=["Death"])\
                        .background_gradient(cmap='Greens',subset=["Recovered"])\
                        .background_gradient(cmap='Purples',subset=["Hospitalization"])

### Bogotá COVID19 map (CONFIRMED CASES)
                        
bog_map = go.Figure(go.Choroplethmapbox(geojson=local_bog,
                                    locations=Localidad_Map['District'],
                                    z=Localidad_Map['Active'],
                                    text = Localidad_Map['text'],
                                    colorscale='matter', zmin=0,
                                    colorbar_title = "Confirmed Cases",
                                    marker_opacity=0.5, marker_line_width=0.2))
bog_map.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=9.5, mapbox_center = {"lat": 4.6097102 , "lon": -74.081749})
bog_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

### Bogotá COVID19 map (RECOVERY MAP)

recovery_map = go.Figure(go.Choroplethmapbox(geojson=local_bog,
                                    locations=Localidad_Map['District'],
                                    z=Localidad_Map['Recovery Rate'],
                                    text = Localidad_Map['text_recover'],
                                    colorscale='greens', zmin=0,
                                    colorbar_title = "Recovery Rate",
                                    marker_opacity=0.5, marker_line_width=0.2))
recovery_map.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=9.5, mapbox_center = {"lat": 4.6097102 , "lon": -74.081749})
recovery_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
