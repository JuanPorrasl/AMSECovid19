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


color_confirmed="#fc5c65"
color_recovered="#45aaf2"
color_deaths="#4b6584"

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
                            md=10,
                        ),
                        dbc.Col(
                            [

                                dcc.DatePickerSingle(
                                    id='map-slider',
                                    min_date_allowed=df.Last_Update.min(),
                                    max_date_allowed=df.Last_Update.max(),
                                    initial_visible_month=df.Last_Update.max(),
                                    date=df.Last_Update.max(),
                                    display_format='D/M/Y',

                                ),
                            ],
                        md=2,
                        ),
                    ],
                    justify="center",
                ),
                fluid=False,
                className="mb-2"
            ),
            #Worldmap
            dbc.Row(
                [
                    dbc.Col([
                                dcc.Loading(
                                    id="loading-1",
                                    type="default",
                                    children=dcc.Graph(id='plot-map', config=config)
                                ),
                        ],
                        md=12,
                    )
                ],
                justify="center",
            ),
            #Dropdown
            dbc.Row(
                [
                    dbc.Col([
                        dcc.Dropdown(
                            id="selected_country",
                            options=dropdown_options,
                            value='Worldwide',
                            className="mb-2 mt-4",
                        ),
                    ],
                    xl=4,
                    ),
                ],
                justify="center",
            ),
            #Cards
            dbc.Row(
                [
                    #Confirmed cases
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                    html.P(["Total Confirmed: ", html.B(id="card-confirmed"),],className="card-text"),         
                            ]),
                            inverse=True,
                            style={"text-align":"center", 'background-color': "#4b6584"}
                        ),
                    ],
                    md=4,
                    ),
                    #Recovered cases card-recovered
                    dbc.Col([  
                        dbc.Card(
                            dbc.CardBody([
                                    html.P(["Total recovered: ", html.B(id="card-recovered"),], className="card-text"),         
                            ]),
                            #Total recovered
                            inverse=True,
                            style={"text-align":"center", 'background-color': "#778ca3"}
                        ),
                    ],
                    md=4,
                    ), 
                    #Deaths cases 
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody([
                                    html.P(["Total deaths: ", html.B(id="card-deaths")], className="card-text"),         
                            ]),
                            #Total deaths
                            inverse=True,
                            style={"text-align":"center", 'background-color': "#a5b1c2"}
                        ),
                    ],
                    md=4,
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
    main_title="Covid19 evolution, {}".format(selected_country)
    
    x_int="{:,}".format(int(df[today & (df["Country_Region"]==selected_country)].Confirmed.sum())).replace(',', ' ')
    y_int="{:,}".format(int(df[today & (df["Country_Region"]==selected_country)].Recovered.sum())).replace(',', ' ')
    z_int="{:,}".format(int(df[today & (df["Country_Region"]==selected_country)].Deaths.sum())).replace(',', ' ')
    return main_title, x_int,y_int,z_int


@app.callback(Output('plot-map', 'figure'),
              [Input('map-slider', 'date')])
def update_map(map_slider):
    df_data=df[(df.Last_Update==map_slider) & (df.Country_Region!="Worldwide")].groupby(['Last_Update', 'Country_Region'], as_index=False)['Confirmed', 'Deaths'].sum()
    
    fig=go.Figure(data=go.Choropleth(
        locations=df_data['Country_Region'],
        #z=np.power(df_data["Confirmed"],0.3)-2,
        z=np.log(df_data["Confirmed"]),
        text=[str(int(elem))+" cases" for elem in df_data["Confirmed"]],
        locationmode='country names',
        colorscale=px.colors.diverging.Spectral,
        autocolorscale=False,
        marker_line_color='#f2f2f2',
        colorbar_title="log(Confirmed cases)",
        reversescale=True,
        zmin=7.5,
        zmax=11.8197782,
    ))

    fig.update_geos(
        projection_type="natural earth",
        showframe=False,
        coastlinecolor="#f2f2f2",
        resolution=110,
        lataxis_showgrid=True, lonaxis_showgrid=True,
        
    )
    
    fig.update_layout(
        height=600,
        xaxis=menu_ranges,
        template="plotly_white",
        margin={"r":0,"l":0,"b":0, "t":0}
    )
    
    
    return fig


@app.callback([Output('daily-cases', 'figure'),Output('daily-cases-recov', 'figure'),Output('daily-cases-deaths', 'figure')],
              [Input('selected_country', 'value')])
def update_daily_cases(selected_country):
    dct = {
        'Confirmed': {'title': 'Daily new cases', 'color': color_confirmed},
        'Recovered': {'title': 'Daily recovered cases', 'color': color_recovered},
        'Deaths': {'title': "Daily new deaths", 'color': color_deaths}
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
        fig.update_layout(xaxis=menu_ranges, template="plotly_white", title_text=dct[col]['title'], yaxis=dict(range=[0, yaxis_max]), height=300, margin={"b":0})
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
        line=dict(color=color_confirmed),
        name="Rate"
    ))
    
    fig.add_trace(go.Scatter(
        x=labels, y=[1]*len(labels),
        line=dict(color=color_deaths, dash='dash'),
        showlegend=False
    ))
    
    fig.update_layout(
        yaxis=dict(range=[0, 3]),
        xaxis=menu_ranges,
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        title_text="Average number of people infected by an infected individual",
        height=300,
        template="plotly_white"
    )
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
                    line_color=color_confirmed,
                    opacity=0.8))
    #Recovered
    fig.add_trace(go.Scatter(
                    x=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Recovered.sum().index,
                    y=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Recovered.sum(),
                    name="Recovered",
                    line_color=color_recovered,
                    opacity=0.8))
    #Deaths
    fig.add_trace(go.Scatter(
                    x=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Deaths.sum().index,
                    y=df[df["Country_Region"]==selected_country].groupby(["Last_Update"]).Deaths.sum(),
                    name="Deaths",
                    line_color=color_deaths,
                    opacity=0.8))
    
    # Add Button
    fig.update_layout(
        xaxis=menu_ranges,
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
    
    fig.update_layout(
        title_text="Cumulative cases evolution", 
        height=300, 
        margin={"b":0}, 
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        template="plotly_white",
    )
    return fig


