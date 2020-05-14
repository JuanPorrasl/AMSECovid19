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

from cleaning_datas_pollution import df, safe_execute, fig_gauge, bar_color, config


#Create badges last update
df_group=df.groupby(["cc_pays","date"], as_index=False).agg({'counter':'sum','calcul':'sum'})
last_date=df_group.groupby("cc_pays").agg({"date":"max"}).to_dict()["date"]
df_group=df_group[df_group.date==[last_date[elem] for elem in df_group.cc_pays]]
badges_updates=[dbc.Badge(str(elem)+": "+last_date[elem].strftime("%d/%m/%y"), style={'background':("#26de81" if ((last_date[elem]==df_group.date.max()) | (last_date[elem]==df_group.date.max())) else "#fed330")}, className="mr-1") for elem in df_group.cc_pays]




#Plot gauges on 120 lasts days
df_group=df.groupby(["cc_pays","cc_region"], as_index=False).agg({'counter':'sum','calcul':'sum'})
df_group["NO2"]=df_group.calcul/df_group.counter

gauge_120days = go.Figure()
fig_gauge(gauge_120days, "Beijing", safe_execute(df_group[(df_group.cc_pays=="CN") & (df_group.cc_region=="Beijing")].NO2.values), 0, 0)
fig_gauge(gauge_120days, "Berlin", safe_execute(df_group[(df_group.cc_pays=="DE") & (df_group.cc_region=="Berlin")].NO2.values), 0, 1)
fig_gauge(gauge_120days, "Milan", safe_execute(df_group[(df_group.cc_pays=="IT") & (df_group.cc_region=="Lombardy")].NO2.values), 0, 2)
fig_gauge(gauge_120days, "Moscow", safe_execute(df_group[(df_group.cc_pays=="RU") & (df_group.cc_region=="Moscow")].NO2.values), 0, 3)
fig_gauge(gauge_120days, "New York", safe_execute(df_group[(df_group.cc_pays=="US") & (df_group.cc_region=="New York")].NO2.values), 1, 0)
fig_gauge(gauge_120days, "Paris", safe_execute(df_group[(df_group.cc_pays=="FR") & (df_group.cc_region=="Ile-de-France")].NO2.values), 1, 1)
fig_gauge(gauge_120days, "Seoul", safe_execute(df_group[(df_group.cc_pays=="KR") & (df_group.cc_region=="Seoul")].NO2.values), 1, 2)
fig_gauge(gauge_120days, "Tokyo", safe_execute(df_group[(df_group.cc_pays=="JP") & (df_group.cc_region=="Tokyo")].NO2.values), 1, 3)
gauge_120days.update_layout(
    height=400,
    title="NO2 average on last 120 days",
    #margin={"r":0,"l":0,"b":0},
    grid = {'rows': 2, 'columns': 4, 'pattern': "independent"})



#Slider values
df_slider=df.date.sort_values(ascending=True).unique()

#Dropdown options
all_options = df[["cc_name","cc_region"]].drop_duplicates().groupby('cc_name')['cc_region'].apply(list).reset_index(name='cc_region').set_index("cc_name").to_dict()["cc_region"]

def create_layout(app):
    body = dbc.Container(
        [
            dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H2("Economic indicators: air quality (NO2)"),
                                    ],
                                    xl=7,
                                    
                                ),
                                dbc.Col(
                                    [
                                        dcc.DatePickerSingle(
                                            id='pick-date-NO2',
                                            min_date_allowed=df.date.min()+pd.Timedelta("5 days"),
                                            max_date_allowed=df.date.max(),
                                            initial_visible_month=df.date.max(),
                                            date=df.date.max(),
                                            display_format='D/M/Y',
                                        ),
                                    ],
                                    xl=2,
                                    
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Latest Updates",
                                            id="collapse-updates-button",
                                            color="light",
                                            block=True,
                                            size="lg",
                                        ),
                                    ],
                                    xl=3,
                                    
                                ),
                            ],
                            justify="center",
                        ),
                ],
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
                                children=dcc.Graph(id='map-NO2', config=config)
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
                                children=dcc.Graph(id='gauge-NO2', config=config)
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
                                dcc.Dropdown(
                                    id="selected_country",
                                    options=[{'label': k, 'value': k} for k in all_options.keys()],
                                    value='FRANCE',
                                    clearable=False, 
                                ),
                            ],
                            xl=3,
                        ),
                    dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="selected_region",
                                ),
                            ],
                            xl=3,
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
                                children=dcc.Graph(id='chart-scatter-NO2', config=config)
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
                                children=dcc.Graph(id='chart-weekofday-NO2', config=config)
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
                                children=dcc.Graph(id='chart-month-NO2', config=config)
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
                                children=dcc.Graph(id='gauge-120days', figure=gauge_120days, config=config)
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


@app.callback(Output('map-NO2', 'figure'),
              [Input('pick-date-NO2', 'date')])
def update_map_NO2(day_selected):
    #Evolution of pollution for some countries
    df_group=df[df.date==day_selected].groupby(["cc_pays"], as_index=False).agg({'counter':'sum','calcul':'sum','cc_name':'max'})
    df_group["NO2"]=df_group.calcul/df_group.counter

    map_NO2 = go.Figure(data=go.Choropleth(
        locations=df_group['cc_name'],
        z=df_group['NO2'],
        locationmode='country names',
        colorscale=px.colors.diverging.Spectral,
        autocolorscale=False,
        marker_line_color='#f2f2f2',
        colorbar_title="NO2",
        reversescale=True,
        zmin=0,
        zmax=0.0001,
    ))
    map_NO2.update_geos(projection_type="natural earth",
                    showocean=False,
                    showframe=False,
                    coastlinecolor="#f2f2f2",
    )
    
    map_NO2.update_layout(height=800,
                      title_text='Last NO2 concentration by countries on '+pd.to_datetime(day_selected, format="%Y-%m-%d").strftime("%d/%m/%Y"),
                      margin={"r":0,"l":0,"b":0})
    return map_NO2



@app.callback([Output('chart-scatter-NO2', 'figure'), Output('chart-weekofday-NO2', 'figure')],
              [Input('selected_country', 'value'),Input('selected_region', 'value')])
def update_scatter_NO2(selected_country, selected_region):
    
    if selected_region is None:
        list_group=["cc_pays","date"]
    else:
        list_group=["cc_pays","cc_region","date"]
        
    df_scatter=df[df.cc_name==selected_country].groupby(list_group, as_index=False).agg({'counter':'sum','calcul':'sum','cc_name':'max'})
    list_group.pop()
    df_scatter["NO2"]=df_scatter.calcul/df_scatter.counter
    
    #Keep values q1 < x 
    quantiles=df_scatter.groupby(list_group)[["counter"]].quantile([.3]).unstack()
    quantiles=pd.DataFrame(quantiles.to_records())
    #Keep values q1 < x 
    quantiles=quantiles.rename(columns={"('counter', 0.3)":"q1"})
    #Merging
    df_scatter=df_scatter.merge(quantiles, left_on=list_group,right_on=list_group,how="left")
    #Removing values
    df_scatter=df_scatter[(df_scatter.counter >= df_scatter.q1)]
    
    if selected_region is None:
        fig = px.line(df_scatter, y="NO2", x="date", template="plotly_white", title="NO2 Evolution of "+selected_country, render_mode="webgl")  
    else:
        fig = px.line(df_scatter[df_scatter.cc_region==selected_region], y="NO2", x="date", template="plotly_white", title="NO2 Evolution of "+selected_region+", "+selected_country, render_mode="webgl") 
    
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
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
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date",
        )
    )
    
    #Bar plot week of day
    if selected_region is not None:
        df_scatter=df_scatter[df_scatter.cc_region==selected_region]
    
    
    fig2 = go.Figure()
    df_scatter["dayofweek"]=df_scatter.date.dt.day_name()
    for elem in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
        df_scatter_day=df_scatter[df_scatter.dayofweek==elem]
        fig2.add_trace(go.Bar(
                        x=df_scatter_day.date,
                        y=df_scatter_day.NO2,
                        text=round((df_scatter_day.NO2.diff()/df_scatter_day.NO2.shift())*100,2).astype(str)+"%",
                        textposition="outside",
                        name=elem,
                        marker_color='#4b6584',
                        visible=(True if elem == "Monday" else False),
                        ))
        fig2.add_trace(go.Scatter(
                        x=df_scatter_day.date,
                        y=df_scatter_day.NO2,
                        name=elem,
                        visible=(True if elem == "Monday" else False),
                        line=dict(color="#fc5c65", dash="dash")))
    
    fig2.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=1,
                y=1.1,
                buttons=list([
                    dict(label="Monday",
                         method="update",
                         args=[{"visible": [True, True, False, False, False, False, False, False, False, False, False, False, False, False]}]),
                    dict(label="Tuesday",
                         method="update",
                         args=[{"visible": [False, False, True, True, False, False, False, False, False, False, False, False, False, False]}]),
                    dict(label="Wednesday",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, True, False, False, False, False, False, False, False, False]}]),
                    dict(label="Thursday",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, True, True, False, False, False, False, False, False]}]),
                    dict(label="Friday",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, False, False, True, True, False, False, False, False]}]),
                    dict(label="Saturday",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, False, False, False, False, True, True, False, False]}]),
                    dict(label="Sunday",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, False, False, False, False, False, False, False, True, True]}]),
                ]),
            )
        ],
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
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
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date",
        )
    )
    
    fig2.update_layout(
        title=(('NO2 evolution by day of week in '+selected_country) if selected_region is None else ('NO2 evolution by day of week in '+selected_region+', '+selected_country)),
        yaxis=dict(
            title='NO2',
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        template="plotly_white",
        barmode='group',
    )
     
    return fig, fig2




#Month 
@app.callback(Output('chart-month-NO2', 'figure'),
              [Input('selected_country', 'value'),Input('selected_region', 'value')])
def update_scatterMonth_NO2(selected_country, selected_region):
    if selected_region is None:
        list_group=["cc_pays",df.date.dt.year, df.date.dt.month]
    else:
        list_group=["cc_pays","cc_region",df.date.dt.year, df.date.dt.month]
        
    df_scatter=df[df.cc_name==selected_country].groupby(list_group, as_index=False).agg({'counter':'sum','calcul':'sum','date':'min'})
    list_group.pop()
    list_group.pop()
    df_scatter["NO2"]=df_scatter.calcul/df_scatter.counter
    
    #Bar plot week of day
    if selected_region is not None:
        df_scatter=df_scatter[df_scatter.cc_region==selected_region]
    
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_scatter.date.dt.to_period('M').dt.to_timestamp(),
        y=df_scatter.NO2,
        text=round((df_scatter.NO2.diff()/df_scatter.NO2.shift())*100,2).astype(str)+"%",
        textposition="outside",
        name="NO2",
        marker_color='#8CABD1',
    ))
    fig.add_trace(go.Scatter(
        x=df_scatter.date.dt.to_period('M').dt.to_timestamp(),
        y=df_scatter.NO2,
        name="NO2",
        line=dict(color="#fc5c65", dash="dash")
    ))
    
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=3,
                         label="3m",
                         step="month",
                         stepmode="backward"),
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
                    dict(step="all")
                ])
            ),
            type="date",
        )
    )
    
    fig.update_layout(
        title=(('NO2 evolution by month in '+selected_country) if selected_region is None else ('NO2 evolution by month in '+selected_region+', '+selected_country)),
        yaxis=dict(
            title='NO2',
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        template="plotly_white",
        barmode='group',
        xaxis_tickformat = '%B %Y'
    )
     
    return fig





@app.callback(Output('gauge-NO2', 'figure'),
              [Input('pick-date-NO2', 'date')])
def update_gauge_NO2(day_selected):
    #Plot daily gauges
    #Evolution of pollution for some regions
    df_group=df[df.date == day_selected].groupby(["cc_pays","cc_region","date"], as_index=False).agg({'counter':'sum','calcul':'sum'})
    df_group["NO2"]=df_group.calcul/df_group.counter
    #Get lastabs date
    last_date=df_group.groupby(["cc_pays","cc_region"]).agg({"date":"max"}).to_dict()["date"]
    df_group=df_group[df_group.date==[last_date[elem] for elem in df_group.set_index(["cc_pays","cc_region"]).index]]
        
    fig = go.Figure()
    fig_gauge(fig, "Beijing", safe_execute(df_group[(df_group.cc_pays=="CN") & (df_group.cc_region=="Beijing")].NO2.values), 0, 0)
    fig_gauge(fig, "Berlin", safe_execute(df_group[(df_group.cc_pays=="DE") & (df_group.cc_region=="Berlin")].NO2.values), 0, 1)
    fig_gauge(fig, "Milan", safe_execute(df_group[(df_group.cc_pays=="IT") & (df_group.cc_region=="Lombardy")].NO2.values), 0, 2)
    fig_gauge(fig, "Moscow", safe_execute(df_group[(df_group.cc_pays=="RU") & (df_group.cc_region=="Moscow")].NO2.values), 0, 3)
    fig_gauge(fig, "New York", safe_execute(df_group[(df_group.cc_pays=="US") & (df_group.cc_region=="New York")].NO2.values), 1, 0)
    fig_gauge(fig, "Paris", safe_execute(df_group[(df_group.cc_pays=="FR") & (df_group.cc_region=="Ile-de-France")].NO2.values), 1, 1)
    fig_gauge(fig, "Seoul", safe_execute(df_group[(df_group.cc_pays=="KR") & (df_group.cc_region=="Seoul")].NO2.values), 1, 2)
    fig_gauge(fig, "Tokyo", safe_execute(df_group[(df_group.cc_pays=="JP") & (df_group.cc_region=="Tokyo")].NO2.values), 1, 3)
    fig.update_layout(
        title="Last NO2 concentration by capitals",
        height=400,
        grid = {'rows': 2, 'columns': 4, 'pattern': "independent"})
    return fig



@app.callback(
    Output('selected_region', 'options'),
    [Input('selected_country', 'value')])
def set_cities_options(selected_country):
    return [{'label': i, 'value': i} for i in all_options[selected_country]]


@app.callback(
    Output('selected_region', 'value'),
    [Input('selected_region', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']