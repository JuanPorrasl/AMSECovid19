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

menu_ranges=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="MTD",
                         step="month",
                         stepmode="todate"),
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=3,
                         label="3m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date"
        )

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

#Create badges last update
badges_updates=covid_state_br.groupby(["state"], as_index=False).agg({"date":"max"})
badges_updates.date=badges_updates.date.dt.strftime('%d/%m/%y')
badges_updates=badges_updates.set_index("state")
badges_updates=badges_updates.to_dict()["date"]
badges_updates=[dbc.Badge(str(elem)+": "+str(badges_updates[elem]), color="secondary", className="mr-1") for elem in badges_updates]
badges_updates.insert(0,"Latest Updates: ")

def create_layout(app):
    body = dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Detailed Brazil analysis"),
    
                        ],
                        xl=10,
                        
                    ),
                    dbc.Col(
                        [
                            dcc.DatePickerSingle(
                                id='days-slider',
                                min_date_allowed=covid_state_br.date.min(),
                                max_date_allowed=covid_state_br.date.max(),
                                initial_visible_month=covid_state_br.date.max(),
                                date=covid_state_br.date.max(),
                                display_format='D/M/Y',
                            ),
                        ],
                        md=2,
                    ),
                ],
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.P(badges_updates)
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
              [Input('days-slider', 'date')])
def update_brazil_map(days_slider):
    fig = go.Figure(go.Choroplethmapbox(
        geojson=states_br, 
        locations=covid_state_br[(covid_state_br.date==days_slider)].codigo_ibg, 
        z=covid_state_br[(covid_state_br.date==days_slider)].confirmed,
        colorscale="OrRd", 
        zmin=0,
        zmax=20000,
        name="",
        text = covid_state_br[(covid_state_br.date==days_slider)]['text'],
        hovertemplate = '<b>State</b>: <b>%{text}</b>'+ '<br><b>Confirmed Cases </b>: %{z}<br>',
        colorbar_title = "Confirmed Cases",
        marker_opacity=0.7, 
        marker_line_width=0
    ))
    
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=2.90, 
        title="Cumulated number of hospitalizations in Brazil on "+pd.to_datetime(days_slider, format="%Y-%m-%d").strftime("%d/%m/%Y"),
        mapbox_center = {"lat": -15.2495, "lon": -51.9253},
        margin={"r":0,"t":30,"l":0,"b":0}
    )
    return fig


@app.callback(Output("tabs-content-br", "figure"), [Input("tabs-br", "active_tab")])
def switch_tab_br(at):
    if at == "tab_2_br":
        # Confirmed cases per 100k habitants
        fig = px.line(covid_state_br, y="confirmed_per_100k_inhabitants", x="date", color="state", render_mode="webgl")
        fig.update_layout(
            title_text="Confirmed cases per 100k/hbts",
            xaxis_title="Timeline",
            yaxis_title="Confirmed cases per 100k/hbts"
        )
        
    else:
        # Confirmed cases
        fig = px.line(covid_state_br, y="confirmed", x="date", color="state", render_mode="webgl")
        fig.update_layout(
            title="Confirmed Cases by Brazilian State",
            xaxis_title="Timeline",
            yaxis_title="Confirmed Cases"
        )
        
    fig.update_layout(
        template="plotly_white", 
        height=600,
        xaxis=menu_ranges,
        margin={"t":80},
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
                x=1,
                xanchor="right",
                y=1,
                yanchor="bottom"
            ),
        ]
    )
        
    return fig