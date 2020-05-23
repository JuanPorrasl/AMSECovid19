import pandas as pd
import json
from datetime import datetime
from urllib.request import urlopen
config = {'displayModeBar': False}

def timer():
    return '['+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+']'

#Downloading dataset
try:
    hospital = pd.read_csv("https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7", sep=";")
    #Save in our repertory
    hospital.to_csv("data/external/france/fr-covid-19.csv", sep=';')
except Exception:
    #If fail, we load our file
    print('\033[1;31;48m'+timer()+'[WARNING] France covid-19 link is not accessible. Reading previous file..')
    hospital = pd.read_csv("data/external/france/fr-covid-19.csv", sep=';')
 
    
hospital=hospital.rename(columns={"dep": "code"})
    
with open("data/processed/france-departements.geojson") as json_file:
    counties = json.load(json_file)
#Fixing id
for i in range(0,len(counties["features"])):
               counties["features"][i]["id"]=counties["features"][i]["properties"]["code"]   
               
today=(hospital.jour==hospital.jour.max())
last_file_france=pd.to_datetime(hospital.jour.max()).strftime("%d/%m/%y")