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

from cleaning_datas_fr import hospital, today, counties, last_file_france, config


#Hospitalisations
df_data=hospital[hospital.sexe!=0].groupby(["jour","sexe"], as_index=False).sum()
graph_hosp = go.Figure()
#Hospitalisations MEN
graph_hosp.add_trace(go.Scatter(
                x=df_data[df_data.sexe==1].jour,
                y=df_data[df_data.sexe==1].hosp,
                name="Men - Hospitalizations",
                line_color='deepskyblue',
                opacity=1))
#Reanimations MEN
graph_hosp.add_trace(go.Scatter(
                x=df_data[df_data.sexe==1].jour,
                y=df_data[df_data.sexe==1].rea,
                name="Men - Respiratory care",
                line_color='orange',
                opacity=1))
#Hospitalisations Women
graph_hosp.add_trace(go.Scatter(
                x=df_data[df_data.sexe==2].jour,
                y=df_data[df_data.sexe==2].hosp,
                name="Women - Hospitalizations",
                line_color='#a6d5fa',
                opacity=1))
#Reanimations Women
graph_hosp.add_trace(go.Scatter(
                x=df_data[df_data.sexe==2].jour,
                y=df_data[df_data.sexe==2].rea,
                name="Women - Respiratory care",
                line_color='#ffdb99',
                opacity=1))
# Use date string to set xaxis range
graph_hosp.update_layout(height=200, template="plotly_white", title_text="Hospitalization evolution in France", margin={"r":0,"t":40,"l":0,"b":0})


#Daily hospitalisation
df_data=hospital[hospital.sexe==0].groupby(["jour","sexe"], as_index=False).sum()
daily_hosp = go.Figure()
#Hospitalisations
daily_hosp.add_trace(go.Bar(
                x=df_data.jour[1:],
                y=df_data.hosp.diff()[1:],
                name="Hospitalizations",
                marker_color='deepskyblue',
                opacity=0.8))

#Reanimations
daily_hosp.add_trace(go.Bar(
                x=df_data.jour[1:],
                y=df_data.rea.diff()[1:],
                name="Respiratory care",
                marker_color='orange',
                opacity=0.8))
# Use date string to set xaxis range
daily_hosp.update_layout(height=200, template="plotly_white", title_text="Daily evolution of the intensive care units and hospitalizations", margin={"r":0,"t":40,"l":0,"b":0})



#Repartition des soins par sexe
df_pie=pd.melt(hospital[(hospital.sexe!=0) & (hospital.jour==hospital.jour.max())].groupby(["jour","sexe"], as_index=False).sum(), id_vars=["sexe"], value_vars=["hosp","rea"])
df_pie.loc[df_pie.sexe==1,"sexe"]="Men"
df_pie.loc[df_pie.sexe==2,"sexe"]="Women"
df_pie.loc[df_pie.variable=="rea","variable"]="Intensive care"
df_pie.loc[df_pie.variable=="hosp","variable"]="Hospitalization"
graph_pie = px.sunburst(df_pie, path=['sexe', 'variable'], values='value', color_discrete_sequence=["#4ba3ed","#ed4ba3"], )




def create_layout(app):
    body = dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Detailed France analysis"),
                            html.P(["Latest Update: ",dbc.Badge("Data Gouv: "+str(last_file_france), color="secondary", className="mr-1")])
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
                            dcc.Slider(
                                id='days-slider',
                                min=0,
                                max=len(hospital.jour.unique())-1,
                                value=len(hospital.jour.unique())-1,
                                marks={days: str(pd.to_datetime(hospital.jour.unique()[days]).strftime("%m/%d")) for days in range(0,len(hospital.jour.unique()), 2)},
                                step=None
                            ),
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
                            html.H5("Number of hospitalizations in France"),
                            
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='france-map', config=config)
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
                                children=dcc.Graph(id='graph-hosp', figure=graph_hosp, config=config)
                            ),
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='daily-hosp', figure=daily_hosp, config=config)
                            ),
                        ],
                        lg=7,
                    ),
                    dbc.Col(
                        [
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='graph_pie', figure=graph_pie, config=config)
                            ),
                        ],
                        lg=5,
                    ),
                ],
                no_gutters=True,
            ),
        ],
        className="mt-4",
    )
                   
    return body



@app.callback(Output('france-map', 'figure'),
              [Input('days-slider', 'value')])
def update_france_map(days_slider):
    fig = go.Figure(go.Choroplethmapbox(geojson=counties, locations=hospital[(hospital.jour==hospital.jour.unique()[days_slider]) & (hospital.sexe==0)].code, z=hospital[(hospital.jour==hospital.jour.unique()[days_slider]) & (hospital.sexe==0)].hosp,
                                        colorscale="OrRd", zmin=0,
                                        marker_opacity=0.7, marker_line_width=0))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=4, mapbox_center = {"lat": 45.0902, "lon": 1.7129})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":15})
    return fig

