import pandas as pd
import numpy as np
import json
from urllib.request import urlopen

config = {'displayModeBar': False}

from cleaning_datas import df

df_US=df[(df["Country_Region"]=="US")]
df_US = df_US.groupby(['Last_Update', 'Country_Region','Province_State'])['Confirmed','Recovered','Deaths'].sum().reset_index()
df_US["Last_Update"] = pd.to_datetime(df_US["Last_Update"]).dt.strftime('%m/%d/%Y')