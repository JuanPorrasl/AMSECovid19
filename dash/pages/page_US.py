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
from cleaning_datas_US import df_US, states_us, Demographic, Deaths_Covid ,Weighted_pop, deaths, Current_State
from cleaning_datas import df, today, yesterday, config

today_US = df_US['Last_Update']==df_US['Last_Update'].max()

df_US_today = df_US[today_US].sort_values(by='Confirmed',ascending=False).drop(columns=['Province_State','Recovered'])
df_US_today = df_US_today[['Last_Update', 'Country_Region', 'State_Code', 'State','Confirmed','Deaths']]

# Data for tests 

Tests = Current_State[['lastUpdateEt','fips','state','state_name', 'totalTestResults', 'positive', 'negative', 'pending']]
Hospital = Current_State[['lastUpdateEt','fips','state','state_name','hospitalized','hospitalizedCurrently','inIcuCurrently','onVentilatorCurrently','hospitalizedCumulative','inIcuCumulative','onVentilatorCumulative']].fillna(0)
Hospital = Hospital.sort_values(by='hospitalizedCurrently',ascending=False).reset_index().drop(columns='index')
Cases = Current_State[['lastUpdateEt','fips','state','state_name','death','recovered']]
rest = Current_State[['fips','state','state_name','dataQualityGrade']]

#Dropdown for states
dropdown_options = [
        {'label':i, 'value': i} for i in deaths['State'].unique()
        ]

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
                    dbc.Col(
                        [
                            html.H3("Covid19 Deaths and Weighted Population Distributions"),
                            html.P("Source: Center for Disease Control and Prevention", style={"font-style":"italic", "color":"grey", "font-size":"small"}),
                            html.P("(*) The weighted population distributions ensure that the population estimates and percentages of COVID-19 deaths represent comparable geographic areas, in order to provide information about whether certain racial and ethnic subgroups are experiencing a disproportionate burden of COVID-19 mortality", style={"font-style":"italic", "color":"grey", "font-size":"small"})
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
                                children=dcc.Graph(id='Covid19-dist',figure=Deaths_Bar, config=config)
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [                            
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='Pop-dist',figure=WPop_bar, config=config)
                            ),
                        ],
                        md=6,
                    ),
                ],
                no_gutters=True,
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Performed Tests by State"),
                            html.P("Source: The Covid Tracking Project", style={"font-style":"italic", "color":"grey", "font-size":"small"}),
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
                                children=dcc.Graph(id='Tests-us', figure=test_us , config=config)
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
                                children=dcc.Graph(id='Hospitalizations-us', figure=hospi_table , config=config)
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
                            html.H3("Total, Covid19 and Pneumonia Deaths"),
                            html.P("Source: Center for Disease Control and Prevention", style={"font-style":"italic", "color":"grey", "font-size":"small"})
                        ],
                        md=12,
                        
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col([
                        dcc.Dropdown(
                            id="selected_country",
                            options=dropdown_options,
                            value='New York City',
                            className="mb-2 mt-4",
                            clearable=False,
                        ),
                    ],
                    xl=4,
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
                                children=dcc.Graph(id='Covid19-deaths', config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
            ),
        ],
        className="mt-4",
    )
                   
    return body


@app.callback(Output('US-map', 'figure'),
              [Input('map-slider', 'value')])
def update_map(map_slider):
        #World Map
    df_data=df_US[(df_US.Last_Update==df_US.Last_Update.unique()[map_slider])].groupby(['Last_Update', 'Country_Region','State_Code','State'], as_index=False)['Confirmed','Recovered', 'Deaths'].sum()
    df_data['text'] = 'State: ' + df_data['State'].astype(str) + '<br>' + \
    'Confirmed: ' + df_data['Confirmed'].astype(str) + '<br>' + \
    'Deaths: ' + df_data['Deaths'].astype(str)  
    
    fig = go.Figure(go.Choroplethmapbox(geojson=states_us, locations=df_data['State_Code'],
                                    z=df_data['Confirmed'],
                                    text=df_data['text'],
                                    colorscale='matter', zmin=0,
                                    colorbar_title = "Confirmed Cases",
                                    #reversescale=True,
                                    marker_opacity=0.5, marker_line_width=0.2))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=3.0, mapbox_center = {"lat": 41.500000, "lon": -100.0})
    fig.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
    return fig

@app.callback(Output('Covid19-deaths', 'figure'),
              [Input('selected_country', 'value')])
def update_deaths(state):
    
    cond = (deaths['State']==state)
    deaths_st = deaths[cond]
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=deaths_st['Start week'],
        y=deaths_st['Total Deaths'],
        name='Total Deaths',
        marker_color='red',
        #connectgaps=True,
        ))
    fig.add_trace(go.Scatter(
        x=deaths_st['Start week'],
        y=deaths_st['COVID-19 Deaths'],
        name='COVID-19 Deaths',
        marker_color='springgreen',
        #connectgaps=True,
        ))
    fig.add_trace(go.Scatter(
        x=deaths_st['Start week'],
        y=deaths_st['Pneumonia Deaths'],
        name='Pneumonia Deaths',
        marker_color='blue',
        #connectgaps=True,
        ))
    
    fig.update_layout(xaxis_rangeslider_visible=True)
    
    return fig


Deaths_Bar = go.Figure(data=[
    go.Bar(name='NH White', y=Deaths_Covid['State'], x=Deaths_Covid['Non-Hispanic White'],orientation='h'),
    go.Bar(name='NH Black or African American', y=Deaths_Covid['State'], x=Deaths_Covid['Non-Hispanic Black or African American'],orientation='h'),
    go.Bar(name='NH American Indian or Alaska Native', y=Deaths_Covid['State'], x=Deaths_Covid['Non-Hispanic American Indian or Alaska Native'],orientation='h'),
    go.Bar(name='NH Asian', y=Deaths_Covid['State'], x=Deaths_Covid['Non-Hispanic Asian'],orientation='h'),
    go.Bar(name='Hispanic or Latino', y=Deaths_Covid['State'], x=Deaths_Covid['Hispanic or Latino'],orientation='h'),
    go.Bar(name='Other', y=Deaths_Covid['State'], x=Deaths_Covid['Other'],orientation='h'),  
])
# Change the bar mode
Deaths_Bar.update_layout(barmode='stack')
Deaths_Bar.update_layout(colorway=px.colors.diverging.Portland)
Deaths_Bar.update_layout(height=860)
#Deaths_Bar.update_layout(showlegend=False)
Deaths_Bar.update_layout(legend_orientation="h")

WPop_bar = go.Figure(data=[
    go.Bar(name='NH White', y=Weighted_pop['State'], x=Weighted_pop['Non-Hispanic White'],orientation='h'),
    go.Bar(name='NH Black or African American', y=Weighted_pop['State'], x=Weighted_pop['Non-Hispanic Black or African American'],orientation='h'),
    go.Bar(name='NH American Indian or Alaska Native', y=Weighted_pop['State'], x=Weighted_pop['Non-Hispanic American Indian or Alaska Native'],orientation='h'),
    go.Bar(name='NH Asian', y=Weighted_pop['State'], x=Weighted_pop['Non-Hispanic Asian'],orientation='h'),
    go.Bar(name='Hispanic or Latino', y=Weighted_pop['State'], x=Weighted_pop['Hispanic or Latino'],orientation='h'),
    go.Bar(name='Other', y=Weighted_pop['State'], x=Weighted_pop['Other'],orientation='h'),  
])
# Change the bar mode
WPop_bar.update_layout(barmode='stack')
WPop_bar.update_layout(colorway=px.colors.diverging.Portland)
WPop_bar.update_layout(height=750)
WPop_bar.update_layout(showlegend=False)

#### Test data

test_us = go.Figure(data=[
    go.Bar(name='Positive', x=Tests['state'], y=Current_State['positive'], text=Tests['state_name']),
    go.Bar(name='Negative', x=Tests['state'], y=Current_State['negative'], text=Tests['state_name'])
])
# Change the bar mode
test_us.update_layout(barmode='stack')
test_us.update_layout(colorway=['orangered','steelblue'])
#test_us.update_layout(showlegend=False)
test_us.update_layout(legend_orientation="h")

## Table hospitalizations

hospi_table = go.Figure(data=[go.Table(
    header=dict(values=['State','Currently Hospitalized', 'Currently in ICU', 'Currently on Ventilator'],
                fill_color='Steelblue',
                font = dict(color = 'white', size = 15),
                align='left'),
    cells=dict(values=[Hospital['state_name'], Hospital['hospitalizedCurrently'], Hospital['inIcuCurrently'], Hospital['onVentilatorCurrently']],
               fill_color='whitesmoke',
               align='left'))
])
