import pandas as pd
import json
from urllib.request import urlopen
config = {'displayModeBar': False}


hospital=pd.read_csv("https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7", sep=";")
hospital=hospital.rename(columns={"dep": "code"})

url="https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
with urlopen(url) as response:
    counties = json.load(response)
#Fixing id
for i in range(0,len(counties["features"])):
               counties["features"][i]["id"]=counties["features"][i]["properties"]["code"]   
               
today=(hospital.jour==hospital.jour.max())