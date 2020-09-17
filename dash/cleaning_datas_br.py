import pandas as pd
import numpy as np
import json
from urllib.request import urlopen
import io
import requests
from datetime import datetime
import os

config = {'displayModeBar': False}

def timer():
    return '['+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+']'

print(timer()+'[INFO] Importing Brazil datas')

brazil_link_folder="data/external/brazil/br-covid-19.csv.gzip"


#Download Brazil Datas
flag_br=0
if os.path.exists(brazil_link_folder):
    file_create=os.path.getmtime(brazil_link_folder)
    file_create=pd.to_datetime(datetime.fromtimestamp(file_create).strftime('%Y-%m-%d'), format='%Y-%m-%d', utc=True)
    if (pd.Timestamp.today(tz="UTC")-file_create >= pd.Timedelta('1 days')):
        flag_br=1
else:
    flag_br=1
    

if flag_br:
    # Downloading the data from Brasil.io
    try:
        response = requests.get("https://data.brasil.io/dataset/covid19/caso_full.csv.gz")
        brazil_data = pd.read_csv(io.BytesIO(response.content), sep=',', compression='gzip')
        brazil_data.to_csv(brazil_link_folder, sep=';', compression='gzip')
    except Exception:
        #If fail, we load our file
        print('\033[1;31;48m'+timer()+'[WARNING] Brazil covid-19 link is not accessible. Reading previous file..')
        brazil_data = pd.read_csv(brazil_link_folder, sep=';',  compression='gzip', index_col=0)
else:
    brazil_data = pd.read_csv(brazil_link_folder, sep=';',  compression='gzip', index_col=0)
    
del flag_br


# Converting date to datetime
brazil_data['date'] = pd.to_datetime(brazil_data['date'], format = '%Y/%m/%d') #errors='ignore'
brazil_data=brazil_data.sort_values("date")
# Generating a dataframe with only data of the states
covid_state_br = brazil_data.loc[brazil_data['place_type'] == "state"]
#Get the a series of latest data for each state is_last == True
last_date = covid_state_br['is_last']

# Loading the coordinates of Brazilian states 
with open("data/processed/brazil-states.geojson") as url_br:
    states_br = json.load(url_br)
    
covid_state_br = covid_state_br.rename(columns={
    "city_ibge_code": "codigo_ibg", 
    "new_deaths":"deaths",
    "new_confirmed":"confirmed", 
    "last_available_confirmed_per_100k_inhabitants": "confirmed_per_100k_inhabitants",
    
})

print(timer()+'[INFO] Successful importation')

#states_br, covid_state_br, last_date