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
from cleaning_datas_US import df_US
from cleaning_datas import df, today, yesterday, config

today_US = df_US['Last_Update']==df_US['Last_Update'].max()
df_US_today = df_US[today_US].sort_values(by='Confirmed',ascending=False).drop(columns=['Province_State','Recovered'])
df_US_today = df_US_today[['Last_Update', 'Country_Region', 'State_Code', 'State','Confirmed','Deaths']]

def create_layout(app):
    body = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("United States Covid19 evolution")
                        ],
                        md=12,
                        
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col([
                                dcc.Loading(
                                    id="loading-1",
                                    type="default",
                                    children=dcc.Graph(id='US-map', config=config)
                                ),
                                
                                dcc.Slider(
                                    id='map-slider',
                                    min=0,
                                    max=len(df_US.Last_Update.unique())-1,
                                    value=len(df_US.Last_Update.unique())-1,
                                    marks={days: str(pd.to_datetime(df_US.Last_Update.unique()[days]).strftime("%m/%d")) for days in range(0,len(df_US.Last_Update.unique()), 7)},
                                    step=None,
                                    className="mt-1"
                                ),
                        ],
                        md=12,
                    ),
                ],
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col([
                            html.H4("Covid19 confirmed and death toll by states"),
                            dbc.Table.from_dataframe(df_US_today),
                        ],
                        md=12,
                    ),
                ],
                justify="center",
            ),      
        ],
        className="mt-4",
    )
                   
    return body


@app.callback(Output('US-map', 'figure'),
              [Input('map-slider', 'value')])
def update_map(map_slider):
        #World Map
    df_data=df_US[(df_US.Last_Update==df_US.Last_Update.unique()[map_slider])].groupby(['Last_Update', 'Country_Region','State_Code'], as_index=False)['Confirmed','Recovered', 'Deaths'].sum()
        
    fig = px.scatter_geo(df_data, locations="State_Code", locationmode = "USA-states",
                         color=np.power(df_data["Deaths"]+1,0.01)-2,
                         size= np.power(df_data["Confirmed"]+50,0.2)-1,
                         hover_name="State_Code",
                         hover_data=["Confirmed","Deaths","Recovered"],
                         animation_frame="Last_Update",
                         scope="usa",
                         )
    fig.update_coloraxes(colorscale="redor")
    fig.update(layout_coloraxis_showscale=False)
    fig.update_geos(
        resolution=110,
        lataxis_showgrid=True, lonaxis_showgrid=True,
        showland=True, landcolor="lightsteelblue",
        showocean=True, oceancolor="lightskyblue",
        showcountries=True, countrycolor="honeydew",
    )
    fig.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
    return fig
