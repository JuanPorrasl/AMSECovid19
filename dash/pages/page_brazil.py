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

from cleaning_datas_br import states_br, covid_state_br, last_date, config

#Fixing id
for i in range(0,len(states_br["features"])):
               states_br["features"][i]["id"] = states_br["features"][i]["properties"]["codigo_ibg"]

# Computing the lethality rate per state (%)
covid_state_br['lethality'] = round((covid_state_br['deaths']/covid_state_br['confirmed'])*100, 2)
covid_state_br['confirmed_per_1Mhab'] = round(covid_state_br['confirmed_per_100k_inhabitants'], 2)

covid_state_br['text'] = 'State: ' + covid_state_br['state'].astype(str) + '<br>' + \
    'Confirmed per 1M Hab.: ' + covid_state_br['confirmed_per_1Mhab'].astype(str) + '<br>' + \
    'Deaths: ' + covid_state_br['deaths'].astype(str) + '<br>' + \
    'Lethality Rate: ' + covid_state_br['lethality'].astype(str) + '%' + '<br>' + \
    'Population (2019): ' + covid_state_br['estimated_population_2019'].astype(str)



def create_layout(app):
    body = dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Detailed Brazil analysis")
                        ],
                        xl=4,
                        
                    ),
                    dbc.Col(
                        [
                            dcc.Slider(
                                id='days-slider',
                                min=0,
                                max=len(covid_state_br.date.unique())-1,
                                value=len(covid_state_br.date.unique())-1,
                                marks={days: str(pd.to_datetime(covid_state_br.date.unique()[days]).strftime("%m/%d")) for days in range(0,len(covid_state_br.date.unique()), 3)},
                                step=None
                            ),
                        ],
                        xl=8,
                    ),
                ],
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H5("Number of hospitalizations in Brazil"),
                            
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='brazil-map', config=config)
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
                            dbc.Tabs(
                                [
                                    dbc.Tab(label="Confirmed cases per state", tab_id="tab_1_br"),
                                    dbc.Tab(label="Confirmed cases for 100k/hbts per state", tab_id="tab_2_br")
                                ],
                                id="tabs-br",
                                active_tab="tab_1_br",
                            ),
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='tabs-content-br', config=config)
                            ),
                            
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
            )
            
        ],
        className="mt-4",
    )
                   
    return body



@app.callback(Output('brazil-map', 'figure'),
              [Input('days-slider', 'value')])
def update_brazil_map(days_slider):

    # Alternative with less DETAILS (consider deleting)
    fig = go.Figure(go.Choroplethmapbox(geojson=states_br, locations=covid_state_br[(covid_state_br.date==covid_state_br.date.unique()[days_slider])].codigo_ibg, z=covid_state_br[(covid_state_br.date==covid_state_br.date.unique()[days_slider])].confirmed,
                                    colorscale="matter", zmin=0,
                                    text = covid_state_br[(covid_state_br.date==covid_state_br.date.unique()[days_slider])]['text'],
                                    #hovertemplate = '<b>State</b>: <b>%{text}</b>'+ '<br><b>Confirmed Cases </b>: %{z}<br>',
                                    colorbar_title = "Confirmed Cases",
                                    marker_opacity=0.3, marker_line_width=0.5))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=2.90, mapbox_center = {"lat": -15.2495, "lon": -51.9253})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig


@app.callback(Output("tabs-content-br", "figure"), [Input("tabs-br", "active_tab")])
def switch_tab_br(at):
    if at == "tab_2_br":
        # Confirmed cases per 100k habitants
        fig = px.line(covid_state_br, y="confirmed_per_100k_inhabitants", x="date", color="state", render_mode="webgl")
        fig.update_layout(title_text="Confirmed cases per 100k/hbts",
                           xaxis_title="Timeline",
                           yaxis_title="Confirmed cases per 100k/hbts")
        
        fig.update_layout(
            updatemenus=[
                dict(
                    type = "buttons",
                    direction = "left",
                    buttons=list([
                        dict(
                            args=["yaxis.type", "linear"],
                            label="Linear",
                            method="relayout"
                        ),
                        dict(
                            args=["yaxis.type", "log"],
                            label="Log",
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
            ]
        )
        return fig
    else:
        # Confirmed cases
        fig = px.line(covid_state_br, y="confirmed", x="date", color="state", render_mode="webgl")
        fig.update_layout(title="Confirmed Cases by Brazilian State",
                           xaxis_title="Timeline",
                           yaxis_title="Confirmed Cases")
        
        fig.update_layout(
            updatemenus=[
                dict(
                    type = "buttons",
                    direction = "left",
                    buttons=list([
                        dict(
                            args=["yaxis.type", "linear"],
                            label="Linear",
                            method="relayout"
                        ),
                        dict(
                            args=["yaxis.type", "log"],
                            label="Log",
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
            ]
        )
        
        return fig