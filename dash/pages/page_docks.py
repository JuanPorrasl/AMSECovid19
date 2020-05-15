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

from cleaning_datas_docks import cargo, last_file_cargo, vessels, last_file_vessels, seacode, config

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
    margin={"b":0},
    height=500,
    template="plotly_white",
    title='Evolution of the number of ships by months in the port of Marseille/Fos',
    yaxis=dict(
        title='Number of vessels',
    ),

    barmode='group',
)
# Add buttons
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


#Plot expeditions
fig_exp = go.Figure()
for i in range(0,2):
    if i==0:
        visibility=False
    else:
        visibility=True
    fig_exp.add_trace(go.Bar(x=cargo[cargo.export==i].groupby("date").sum().index,
                    y=cargo[cargo.export==i].groupby("date").sum().FOS,
                    name='FOS',
                    visible=visibility,
                    marker_color='rgb(55, 83, 109)'
                    ))
    fig_exp.add_trace(go.Bar(x=cargo[cargo.export==i].groupby("date").sum().index,
                    y=cargo[cargo.export==i].groupby("date").sum().MRS,
                    name='MRS',
                    visible=visibility,
                    marker_color='rgb(26, 118, 255)'
                    ))

fig_exp.update_layout(
    height=500,
    margin={"b":0},
    template="plotly_white",
    title='Number of expeditions imports-exports at Marseille/Fos docks',
    yaxis=dict(
        title='Quantities',
    ),

    barmode='group',
)
# Add buttons
fig_exp.update_layout(
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

fig_exp.update_layout(
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
            x=1.21,
            xanchor="right",
            y=1.10,
            yanchor="bottom",
            buttons=list([
                dict(label="Exports",
                     method="update",
                     args=[{"visible": [False, False, True, True]}]),
                dict(label="Imports",
                     method="update",
                     args=[{"visible": [True, True, False, False]}]),
            ]),
        ),
    ],
    
)

colors_palet={'ITALY':"#fad390", 'TURKEY':"#f8c291", 'SPAIN':"#ff6b81", 'FRANCE':"#82ccdd", 'SLOVENIA':"#b8e994", 'MOROCCO':"#f6b93b",
       'PORTUGAL':"#e55039", 'TUNISIA':"#4a69bd", 'ALGERIA':"#78e08f", 'UNITED STATES OF AMERICA':"#60a3bc",
       'ISRAEL':"#747d8c", 'MALTA':"#70a1ff", 'GREECE':"#786fa6", 'BENIN':"#D980FA", 'JORDAN':"#B53471", 'EGYPT':"#6F1E51", 'SENEGAL':"#C4E538",
       'ROMANIA':"#fa983a", 'NIGERIA':"#eb2f06", 'BELGIUM':"#1e3799", 'LIBYA':"#3c6382", 'NETHERLANDS':"#38ada9", 'CANADA':"#e58e26",
       "CÔTE D'IVOIRE":"#b71540", 'GHANA':"#0c2461", 'GIBRALTAR':"#0a3d62", 'SINGAPORE':"#079992", 'GERMANY':"#fad390",
       'FRENCH GUIANA':"#f8c291"}

#Fig last pos
#Link informations previous and next port
vessels=vessels.merge(seacode, left_on="cal_last_place_code", right_on="CODE", how="left").rename(columns={"Country":"country_last", "Port":"port_last", "latitude":"latitude_last", "longitude":"longitude_last"})
vessels=vessels.merge(seacode, left_on="cal_next_place_code", right_on="CODE", how="left").rename(columns={"Country":"country_next", "Port":"port_next", "latitude":"latitude_next", "longitude":"longitude_next"})
vessels=vessels.rename(columns={"CODE_x":"CODE_last", "CODE_y":"CODE_next"})
#Groups for plot
vessels_groups=vessels.groupby([vessels.date.dt.year, vessels.date.dt.month, "country_last","port_last"], as_index=False).agg({'counter': 'sum', 'cal_diff': 'mean', 'date':'max'})
#Remove if obs < 2018 and if date < today
vessels_groups=vessels_groups[(vessels_groups.date > "2018-01-01") & (vessels_groups.date.dt.date <= pd.Timestamp.today())]
#Manipulation to get full horizontal bar chart
vessels_groups=vessels_groups.merge(vessels_groups.groupby("date", as_index=False)[["date","counter"]].sum(), left_on="date", right_on="date", how="left").rename(columns={"counter_x":"counter","counter_y":"sum_day"})
vessels_groups["counter_rel"]=vessels_groups.counter/vessels_groups.sum_day

fig_last_pos = px.bar(vessels_groups, x="counter_rel", color_discrete_map=colors_palet, y="date", color="country_last", title="Previous position of the ship", template="plotly_white", orientation='h')
fig_last_pos.update_layout(
    height=550,
    yaxis=dict(
        title='date',
    ),
    xaxis=dict(
        title='distribution',
    ),
)


#Fig next pos
#Groups for plot
vessels_groups=vessels.groupby([vessels.date.dt.year, vessels.date.dt.month, "country_next","port_next"], as_index=False).agg({'counter': 'sum', 'cal_diff': 'mean', 'date':'max'})
#Remove if obs < 2018 and if date < today
vessels_groups=vessels_groups[(vessels_groups.date > "2018-01-01") & (vessels_groups.date.dt.date <= pd.Timestamp.today())]

#Manipulation to get full horizontal bar chart
vessels_groups=vessels_groups.merge(vessels_groups.groupby("date", as_index=False)[["date","counter"]].sum(), left_on="date", right_on="date", how="left").rename(columns={"counter_x":"counter","counter_y":"sum_day"})
vessels_groups["counter_rel"]=vessels_groups.counter/vessels_groups.sum_day

fig_next_pos = px.bar(vessels_groups, x="counter_rel", y="date", color="country_next", color_discrete_map=colors_palet, title="Next position of the ship", template="plotly_white", orientation='h')
fig_next_pos.update_layout(
    height=550,
    yaxis=dict(
        title='date',
    ),
    xaxis=dict(
        title='distribution',
    ),
)


def create_layout(app):
    body = dbc.Container(
        [
            dbc.Container(
                #DROPDOWN MENU
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2("Economic indicators: maritime trade"),
                                html.P(["Latest Updates: ",dbc.Badge("Cargo: "+str(last_file_cargo), color="secondary", className="mr-1"), dbc.Badge("Vessels: "+str(last_file_vessels), color="secondary", className="mr-1")])
                            ],
                            xl=12,
                            
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
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='vessels_number', figure=vessels_number, config=config)
                            ),
                            html.P("(*) Values that are higher than today correspond to planned records and are bound to change.", style={"font-style":"italic", "color":"grey", "font-size":"small", "margin-left":"80px"})
                        ],
                        lg=12,  
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
                                children=dcc.Graph(id='fig_exp', figure=fig_exp, config=config),
                            ),
                        ],
                        lg=12,
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
                                children=dcc.Graph(id='fig_next_pos', figure=fig_next_pos, config=config)
                            ),
                        ],
                        lg=12,
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
                                children=dcc.Graph(id='fig_last_pos', figure=fig_last_pos, config=config)
                            ),
                        ],
                        lg=12,
                    ),
                ],
                no_gutters=True,
            ),
        ],
        className="mt-4",
        fluid=True
    )
                   
    return body




