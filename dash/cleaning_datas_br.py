import pandas as pd
import numpy as np
import json
from urllib.request import urlopen

config = {'displayModeBar': False}


# Downloading the data from Brasil.io
brazil_data = pd.read_csv("https://data.brasil.io/dataset/covid19/caso.csv.gz", sep=",")
# Converting date to datetime
brazil_data['date'] = pd.to_datetime(brazil_data['date'], format = '%Y/%m/%d') #errors='ignore'
brazil_data=brazil_data.sort_values("date")
# Generating a dataframe with only data of the states
covid_state_br = brazil_data.loc[brazil_data['place_type'] == "state"]
#Get the a series of latest data for each state is_last == True
last_date = covid_state_br['is_last']

# Downloading the coordinates of Brazilian states
url_br="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
with urlopen(url_br) as response_br:
    states_br = json.load(response_br)
    
covid_state_br = covid_state_br.rename(columns={"city_ibge_code": "codigo_ibg"})

#states_br, covid_state_br, last_date