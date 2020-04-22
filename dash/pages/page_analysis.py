import os

import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State 

from app import app
import plotly.graph_objects as go

from cleaning_datas import df, config

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
                            html.H2("Global analysis")
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
            )
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
        