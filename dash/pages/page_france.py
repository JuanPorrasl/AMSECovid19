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


#Hospitalisations
df_data=hospital[hospital.sexe!=0].groupby(["jour","sexe"], as_index=False).sum()
graph_hosp = go.Figure()
#Hospitalisations MEN
graph_hosp.add_trace(go.Scatter(
                x=df_data[df_data.sexe==1].jour,
                y=df_data[df_data.sexe==1].hosp,
                name="Men - Hospitalizations",
                line_color='#45aaf2',
                opacity=1))
#Reanimations MEN
graph_hosp.add_trace(go.Scatter(
                x=df_data[df_data.sexe==1].jour,
                y=df_data[df_data.sexe==1].rea,
                name="Men - Respiratory care",
                line_color='#fd9644',
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
graph_hosp.update_layout(
    xaxis=menu_ranges,
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0.5)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    template="plotly_white", 
    title_text="Hospitalization evolution in France", 
)


#Daily hospitalisation
df_data=hospital[hospital.sexe==0].groupby(["jour","sexe"], as_index=False).sum()
daily_hosp = go.Figure()
#Hospitalisations
daily_hosp.add_trace(go.Bar(
    x=df_data.jour[1:],
    y=df_data.hosp.diff()[1:],
    name="Hospitalizations",
    marker_color='#45aaf2',
    opacity=0.8)
)

#Reanimations
daily_hosp.add_trace(go.Bar(
    x=df_data.jour[1:],
    y=df_data.rea.diff()[1:],
    name="Respiratory care",
    marker_color='#fd9644',
    opacity=0.8)
)

daily_hosp.update_layout(
    xaxis=menu_ranges,
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
            x=1,
            xanchor="right",
            y=1,
            yanchor="bottom"
        ),
    ],
    legend=dict(
        x=0,
        y=1,
        bgcolor='rgba(255, 255, 255, 0.5)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    template="plotly_white", 
    title_text="Daily evolution of the intensive care units and hospitalizations", 
)



#Repartition des soins par sexe
df_pie=pd.melt(hospital[(hospital.sexe!=0) & (hospital.jour==hospital.jour.max())].groupby(["jour","sexe"], as_index=False).sum(), id_vars=["sexe"], value_vars=["hosp","rea"])
df_pie.loc[df_pie.sexe==1,"sexe"]="Men"
df_pie.loc[df_pie.sexe==2,"sexe"]="Women"
df_pie.loc[df_pie.variable=="rea","variable"]="Intensive care"
df_pie.loc[df_pie.variable=="hosp","variable"]="Hospitalization"
graph_pie = px.sunburst(df_pie, path=['sexe', 'variable'], values='value', color_discrete_sequence=["#2d98da","#ff6b81"], title="Distribution in hospitals by sex")




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
                        md=10,
                    ),
                    dbc.Col(
                        [
                            dcc.DatePickerSingle(
                                id='days-slider',
                                min_date_allowed=hospital.jour.min(),
                                max_date_allowed=hospital.jour.max(),
                                initial_visible_month=hospital.jour.max(),
                                date=hospital.jour.max(),
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
                        ],
                        lg=12,
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
                                children=dcc.Graph(id='daily-hosp', figure=daily_hosp, config=config)
                            ),
                        ],
                        lg=12,
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
                                children=dcc.Graph(id='graph_pie', figure=graph_pie, config=config)
                            ),
                        ],
                        lg=6,
                    ),
                ],
                justify="center",
                no_gutters=True,
            ),
        ],
        className="mt-4",
    )
                   
    return body



@app.callback(Output('france-map', 'figure'),
              [Input('days-slider', 'date')])
def update_france_map(days_slider):
    fig = go.Figure(go.Choroplethmapbox(
        geojson=counties, 
        locations=hospital[(hospital.jour==days_slider) & (hospital.sexe==0)].code, 
        z=hospital[(hospital.jour==days_slider) & (hospital.sexe==0)].hosp,
        colorscale="OrRd", 
        zmin=0,
        zmax=1000,
        marker_opacity=0.8, 
        marker_line_width=0
    ))
    
    fig.update_layout(
        height=800,
        mapbox_style="carto-positron",
        mapbox_zoom=5, 
        mapbox_center = {"lat": 45.9902, "lon": 1.7129},
        margin={"r":0,"l":0, "b":0, "t":30},
        title="Number of hospitalizations in France on "+pd.to_datetime(days_slider, format="%Y-%m-%d").strftime("%d/%m/%Y"),
    )
    return fig

