import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
def timer():
    return '['+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+']'

from data.processed.country_code import CC #Edit when importing on the dashboard
config = {'displayModeBar': False}

path="data/external/datas_sentinel5/"


#Help plotting gauges
def bar_color(x):
    if x <= 0.000020:
        bar_value={ 'color': "#2bcbba", 'thickness':1 }
    elif (x>0.000020) & (x<=0.000040):
        bar_value={ 'color': "#26de81", 'thickness':1 }
    elif (x>0.000040) & (x<=0.000060):
        bar_value={ 'color': "#fed330", 'thickness':1 }
    elif (x>0.000060) & (x<=0.000080):
        bar_value={ 'color': "#fd9644", 'thickness':1 }
    else:
        bar_value={ 'color': "#fc5c65", 'thickness':1 }
    return bar_value

#Help plotting gauges
def fig_gauge(fig, country_name, NO2, row=0, col=0):
    return fig.add_trace(go.Indicator(
    domain = {'row': row, 'column': col},
    value = NO2,
    mode = "gauge+number+delta",
    title = {'text': country_name},
    gauge = {'axis': {
        'visible':False,
        'range': [None, 0.0001]
    },
             'bar': bar_color(NO2),
             'bordercolor':"white"
            }))

#Handle errors if row not available for a day (Gauge plot)
def safe_execute(x):
    if len(x) > 0:
        return x[0]
    else:
        return float("NaN")

print(timer()+'[INFO] Import air polution datas, this step can take a while...')
#Get 120 lasts days
max_day=[elem.strftime("archived_%Y_%m_%d.csv") for elem in pd.to_datetime(pd.Series(os.listdir(path+"archives/")), format="archived_%Y_%m_%d.csv").sort_values(ascending=False).reset_index(drop=True)[0:120]]
max_day=[elem.split("_") for elem in max_day]
max_day=[[elem.lstrip("0") for elem in max_day[i]] for i in range(0,len(max_day))]
max_day=["_".join(max_day[i]) for i in range(0,len(max_day))]

try:
    df
except NameError:
    #Load file 120 lasts files
    df=pd.DataFrame()
    for elem in max_day:
        df=pd.concat([df,pd.read_csv(path+"archives/"+elem, index_col=0)])
    df=df.reset_index(drop=True)
    #Re-arranging date
    df=df.rename(columns={"day_mean":"day"})
    df["date"]=pd.to_datetime(df[["year","month","day"]])
    df=df.drop(columns=["year","month","day"])
    #Columns for weighted computation
    df["calcul"]=df.NO2*df.counter
    #Put full names for countries
    df["cc_name"]=[CC[elem] if elem != "Undefined" else "" for elem in df.cc_pays]
    print(timer()+'[INFO] Successful importation')
    