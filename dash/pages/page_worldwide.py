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
from cleaning_datas import df, today, yesterday, last_file_hopkins, config

############# PLOT PART #############
#Dropdown for neighbourhood
dropdown_options = [
        {'label':i, 'value': i} for i in df["Country_Region"].unique()
        ]

body_worldwide = dbc.Container(
        [
            dbc.Container(
                #DROPDOWN MENU
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2(id="title-main"),
                                html.P(["Latest Updates: ",dbc.Badge("Hopkins: "+str(last_file_hopkins), color="secondary", className="mr-1")])
                            ],
                            md=9,
                        ),
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="selected_country",
                                    options=dropdown_options,
                                    value='Worldwide',
                                    clearable=False
                                ),
                            ],
                            md=3,
                        )
                    ],
                    justify="center",
                ),
                fluid=False,
                className="mb-2"
            ),
            #Cards
            dbc.Row(
                [
                    dbc.Col(
                        [
                        dbc.Card(
                            dbc.CardBody([
                                    html.P("Total Confirmed", className="card-title"),
                                    html.H4(id="card-confirmed", className="card-text"),
                            ]),
                            #Total confirmed,
                            inverse=True, className="mb-1",
                            style={"text-align":"center", 'background-color': "#384259"}
                        ),
                        dbc.Card(
                            dbc.CardBody([
                                    html.P("Total Recovered", className="card-title"),
                                    html.H4(id="card-recovered", className="card-text"),
                            ]),
                            #Total recovered
                            inverse=True, className="mb-1",
                            style={"text-align":"center", 'background-color': "#7ac7c4"}
                        ),
                        dbc.Card(
                            dbc.CardBody([
                                    html.P("Total Deaths", className="card-title"),
                                    html.H4(id="card-deaths", className="card-text"),
                            ]),
                            #Total deaths
                            inverse=True, className="mb-2",
                            style={"text-align":"center", 'background-color': "#f73859"}
                        )
                        ],
                        md=4,
                    ),
                    dbc.Col([
                                dcc.Loading(
                                    id="loading-1",
                                    type="default",
                                    children=dcc.Graph(id='plot-map', config=config)
                                ),
                                
                                dcc.Slider(
                                    id='map-slider',
                                    min=0,
                                    max=len(df.Last_Update.unique())-1,
                                    value=len(df.Last_Update.unique())-1,
                                    marks={days: str(pd.to_datetime(df.Last_Update.unique()[days]).strftime("%m/%d")) for days in range(0,len(df.Last_Update.unique()), 7)},
                                    step=None,
                                    className="mt-1"
                                ),
                        ],
                        md=8,
                    )
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
                                children=dcc.Graph(id='daily-cases', config=config)
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='cumulative-cases', config=config)
                            ),
                        ],
                        md=6,
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
                                children=dcc.Graph(id='daily-cases-recov', config=config)
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='daily-cases-deaths', config=config)
                            ),
                        ],
                        md=6,
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
                                children=dcc.Graph(id='infection-cases', config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
                no_gutters=True,
            ),
        ],
        className="mt-4",
        fluid=True
    )


                        
                        
                            
                            

@app.callback([Output('title-main', 'children'), Output('card-confirmed', 'children'), Output('card-recovered', 'children'), Output('card-deaths', 'children')],
              [Input('selected_country', 'value')])
def main_bar(selected_country):
    main_title="{} evolution".format(selected_country)
    
    x_int="{:,}".format(int(df[today & (df["Country_Region"]==selected_country)].Confirmed.sum())).replace(',', ' ')
    y_int="{:,}".format(int(df[today & (df["Country_Region"]==selected_country)].Recovered.sum())).replace(',', ' ')
    z_int="{:,}".format(int(df[today & (df["Country_Region"]==selected_country)].Deaths.sum())).replace(',', ' ')
    return main_title, x_int,y_int,z_int


@app.callback(Output('plot-map', 'figure'),
              [Input('map-slider', 'value')])
def update_map(map_slider):
        #World Map
    df_data=df[(df.Last_Update==df.Last_Update.unique()[map_slider])].groupby(['Last_Update', 'Country_Region'], as_index=False)['Confirmed', 'Deaths'].sum()
        
    fig = px.scatter_geo(df_data, locations="Country_Region", locationmode = "country names",
                         color=np.power(df_data["Confirmed"],0.3)-2, size= np.power(df_data["Confirmed"]+1,0.3)-1,
                         hover_name="Country_Region",
                         hover_data=["Confirmed"],
                         animation_frame="Last_Update",
                         projection="natural earth")
    fig.update_coloraxes(colorscale="redor")
    fig.update(layout_coloraxis_showscale=False)
    fig.update_geos(
        resolution=110,
        lataxis_showgrid=True, lonaxis_showgrid=True,
        showland=True, landcolor="palegreen",
        showocean=True, oceancolor="lightskyblue",
        showcountries=True, countrycolor="honeydew",
    )
    fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})
    return fig


@app.callback([Output('daily-cases', 'figure'),Output('daily-cases-recov', 'figure'),Output('daily-cases-deaths', 'figure')],
              [Input('selected_country', 'value')])
def update_daily_cases(selected_country):
    dct = {
        'Confirmed': {'title': 'Daily new cases', 'color': '#384259'},
        'Recovered': {'title': 'Daily recovered cases', 'color': '#7ac7c4'},
        'Deaths': {'title': "Daily new deaths", 'color': '#f73859'}
    }
    df_data=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).sum()
    labels=df_data.index[1:]
    values=df_data.diff()     
    def bar_graph(values, col):
        yaxis_max = values[col].max()*1.1
        fig = go.Figure(
            data=[go.Bar(x=labels, y=values[col].tolist())],
            layout_title_text=dct[col]['title']
        )
        fig.update_traces(marker_color=dct[col]['color'])
        fig.update_layout(title_text=dct[col]['title'], yaxis=dict(range=[0, yaxis_max]), height=300, margin={"b":0})
        return fig
    graphs = {col: bar_graph(values, col) for col in dct.keys()}    
    return graphs['Confirmed'], graphs['Recovered'], graphs['Deaths']


@app.callback(Output('infection-cases', 'figure'),
              [Input('selected_country', 'value')])
def infection_cases(selected_country):
    gauss_kernel = Gaussian1DKernel(4)
    
    df_data=df[df.Country_Region==selected_country].groupby(["Last_Update"])["Confirmed"].sum().diff()
    labels=pd.to_datetime(df_data.index[1:])
    
    values=(convolve(df_data[1:], gauss_kernel)/convolve(df_data[1:].shift(5), gauss_kernel))[5:]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels[7:], y=values,
        line=dict(color='red'),
        name="Rate"
    ))
    
    fig.add_trace(go.Scatter(
        x=labels, y=[1]*len(labels),
        line=dict(color='green', dash='dash'),
        showlegend=False
    ))
    
    # Add range slider
    fig.update_layout(
        yaxis=dict(range=[0, 3]),
        xaxis=dict(
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
    )
    fig.update_layout(title_text="Average number of people infected by an infected individual", height=300, margin={"b":0})
    return fig


@app.callback(Output('cumulative-cases', 'figure'),
              [Input('selected_country', 'value')])
def update_cumulative_cases(selected_country):
    fig = go.Figure()
    #Confirmed
    fig.add_trace(go.Scatter(
                    x=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Confirmed.sum().index,
                    y=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Confirmed.sum(),
                    name="Confirmed",
                    line_color='#384259',
                    opacity=0.8))
    #Recovered
    fig.add_trace(go.Scatter(
                    x=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Recovered.sum().index,
                    y=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Recovered.sum(),
                    name="Recovered",
                    line_color='#7ac7c4',
                    opacity=0.8))
    #Deaths
    fig.add_trace(go.Scatter(
                    x=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Deaths.sum().index,
                    y=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Deaths.sum(),
                    name="Deaths",
                    line_color='#f73859',
                    opacity=0.8))
    
    # Use date string to set xaxis range
    fig.update_layout(title_text="Cumulative cases evolution", height=300, margin={"b":0})
    
    # Add Button
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


