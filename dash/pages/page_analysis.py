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

from cleaning_datas import df, last_file_hopkins, config, df_pop

## Ratios plots
df_data=pd.DataFrame(df.groupby(["Country_Region","Last_Update"]).sum())
df_data["ratio"]=100*df.groupby(["Country_Region","Last_Update"]).Deaths.sum()/df.groupby(["Country_Region","Last_Update"]).Confirmed.sum()
df_data[np.isnan(df_data['ratio'])]=0

df_data["ratio_2"]=100*(df.groupby(["Country_Region","Last_Update"]).Recovered.sum()+df.groupby(["Country_Region","Last_Update"]).Deaths.sum())/df.groupby(["Country_Region","Last_Update"]).Confirmed.sum()
df_data[np.isnan(df_data['ratio_2'])]=0

countries={"China":"#FF9671","France":"#845EC2","Italy":"#D65DB1","US":"#FF6F91","Russia":"#2C73D2","Germany":"#00C9A7","United Kingdom":"#B0A8B9"}


#Generating tables
df_tables=df_data.reset_index()
classement=df_tables[(df_tables.Last_Update==df_tables.Last_Update.max()) & (df_tables.Confirmed>=100)]
classement=classement.rename(columns={"Country_Region":"Countries","ratio":"Lethality rates", "ratio_2":"rates"})
classement["Lethality rates"]=classement["Lethality rates"].round(2)
classement["rates"]=classement["rates"].round(2)

def create_layout(app):
    body = dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Global analysis"),
                            html.P(["Latest Updates: ",dbc.Badge("Hopkins: "+str(last_file_hopkins), color="secondary", className="mr-1")])
                        ],
                        md=12,
                        
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H5("Highest fatality rates*"),
                            dbc.Table.from_dataframe(classement.sort_values(["Lethality rates"], ascending=False).head()[["Countries","Lethality rates"]], striped=True, bordered=True, hover=True, size="sm", style={"margin-bottom":"0"}),
                            html.P("(*) Countries with less than 100 cases are excluded", style={"font-style":"italic", "color":"grey", "font-size":"small"})
                        ],
                        lg=4,
                    ),
                    dbc.Col(
                        [
                            html.H5("Highest cure and death rates"),
                            dbc.Table.from_dataframe(classement.sort_values(["rates"], ascending=False).head()[["Countries","rates"]], striped=True, bordered=True, hover=True, size="sm")
                        ],
                        lg=4,
                    ),
                    dbc.Col(
                        [
                            html.H5("Highest number of deaths"),
                            dbc.Table.from_dataframe(classement.sort_values(["Deaths"], ascending=False)[["Countries","Deaths"]][1:6], striped=True, bordered=True, hover=True, size="sm")
                        ],
                        lg=4,
                    ),
                ],
            ),
            dbc.Row(
                [
                     dbc.Col(
                         [
                            dbc.Tabs(
                                [
                                    dbc.Tab(label="Deaths/Confirmed cases", tab_id="tab_1"),
                                    dbc.Tab(label="Recovered & Deaths/Confirmed cases", tab_id="tab_2")
                                ],
                                id="tabs",
                                active_tab="tab-1",
                            ),
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='tabs-content', config=config)
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
                                children=dcc.Graph(id='pop_density',figure=pd_fig, config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H5("Countries by population (Covid19 death and confirmed cases)")
                        ],
                        md=12,
                    ),
                    dbc.Col(
                        [
                        dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=dcc.Graph(id='pop_cases',figure=pop_fig, config=config)
                            ),
                        ],
                        md=12,
                    ),
                ],
            ),
        ],
        className="mt-4"
    )
                   
    return body


@app.callback(Output("tabs-content", "figure"), [Input("tabs", "active_tab")])
def switch_tab(at):
    if at == "tab_2":
        ## reco_death_conf_ratio
        fig = go.Figure()
        for elem in countries:
            fig.add_trace(go.Scatter(
                            x=df_data.loc[elem].index,
                            y=df_data.loc[elem].ratio_2,
                            name=elem,
                            line_color=countries[elem],
                            opacity=0.8))
        fig.update_layout(height=400, title_text="Recovered & Deaths/Confirmed ratio")
        return fig
    else:
        ## death_conf_ratio
        fig = go.Figure()
        for elem in countries:
            fig.add_trace(go.Scatter(
                            x=df_data.loc[elem].index,
                            y=df_data.loc[elem].ratio,
                            name=elem,
                            line_color=countries[elem],
                            opacity=0.8))
        fig.update_layout(height=400, title_text="Deaths/Confirmed ratio")
        return fig
   
# Cases, deaths and total population
pop_fig = px.treemap(df_pop, path=['Country_Region','Confirmed','Deaths'], values='PopTotal',
                     color='Deaths',
                     color_continuous_scale='Reds')
pop_fig.update_layout(height=800, margin={"r":0,"t":0,"l":0,"b":0})

#Population Density

pd_fig = px.choropleth(df_pop, locations="Country_Region",
                    color=np.power(df_pop["PopDensity"],0.1), # lifeExp is a column of gapminder
                    hover_name="Country_Region", # column to add to hover information
                    hover_data=['PopDensity','PopTotal',"Confirmed/Pop",'Confirmed','Deaths','Recovered'],
                    color_continuous_scale=px.colors.sequential.Plasma,locationmode="country names")
pd_fig.update_geos(fitbounds="locations", visible=False)
pd_fig.update_layout(title_text="Population Density (Population per square kilometer)")
pd_fig.update_coloraxes(colorbar_title="Pop Density (Log Scale)",colorscale="Magma_r")
pd_fig.update_layout(coloraxis_showscale=False)

