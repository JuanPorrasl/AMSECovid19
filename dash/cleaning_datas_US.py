import pandas as pd
import io
import requests
import os
import time

import plotly.express as px
import plotly.graph_objects as go

from urllib.request import urlopen
import json

print('Chargement US')
pd.set_option('display.max_columns', None)

def pd_load(url, path):
    #Check if file available 
    file=url.split("/")
    current_time = time.time()
    
    if (file[-1] not in os.listdir(path)) or (((current_time-os.path.getmtime(path+url.split("/")[-1]))/60/60) > 24):
        s=requests.get(url).content
        df=pd.read_csv(io.StringIO(s.decode('utf-8')))
        #Save
        df.to_csv(path+file[-1], index=False)
    else:
        df=pd.read_csv(path+file[-1])
        
    return df


config = {'displayModeBar': False}

df=pd_load("https://static.usafacts.org/public/data/covid-19/covid_confirmed_usafacts.csv","data/external/US/")
#Transform to text
df["countyFIPS"]=df["countyFIPS"].astype(str)
#Fix 0 for 1 number codes
df.countyFIPS=df.countyFIPS.str.zfill(5)

df.columns=list(df.columns[:4])+list(pd.to_datetime(df.columns[4:], format='%m/%d/%y').strftime("%Y-%m-%d"))

last_day=df.columns[len(df.columns)-1]
first_day=df.columns[4]

df_state=df.copy()

popUS=pd.read_csv("data/external/US/co-est2019-alldata.csv", encoding="UTF-8", sep=",", usecols=["STATE","COUNTY","POPESTIMATE2019"])

for elem in ["STATE","COUNTY"]:
    popUS[elem]=popUS[elem].astype(str)
    
#Fix format zfill
popUS.STATE=popUS.STATE.str.zfill(2)
popUS.COUNTY=popUS.COUNTY.str.zfill(3)

popUS["countyFIPS"]=popUS.STATE+popUS.COUNTY
popUS=popUS.drop(columns=["STATE","COUNTY"])

#Add pop
df=df.merge(popUS, on="countyFIPS", how="left")
#Remove NA rows
df=df[~df.POPESTIMATE2019.isna()]

df.loc[:,df.columns[4:-1]]=round(100*(df[df.columns[4:-1]].transpose()/df.POPESTIMATE2019.values).transpose(),2)

#Load US results
US_results=pd.read_csv("data/external/US/US_results20Bis.csv", sep=";")

#AJoute tot vote par States
US_results_states=US_results.groupby(["stateFips","fullName"])["vote"].sum().reset_index()

temp=US_results_states.groupby(["stateFips"])["vote"].sum().reset_index()
temp=temp.rename(columns={"vote":"tot_county_votes"})
US_results_states=US_results_states.merge(temp, on="stateFips", how="left")
#Ajoute pct
US_results_states["votePct"]=(100*US_results_states["vote"]/US_results_states["tot_county_votes"])
US_results_states.votePct=US_results_states.votePct.astype("double").round(2)


#Gagnant pour States 

US_results_states=US_results_states.merge(df[["stateFIPS","State"]].drop_duplicates(), left_on="stateFips", right_on="stateFIPS", how="left").drop(columns=["stateFIPS"])
#Keep max per countyFipsCode
temp=US_results_states.groupby("stateFips")["votePct"].max().reset_index()
temp["check"]=1
#Keep only winner
US_results_states=US_results_states[~(US_results_states.merge(temp, on=["stateFips","votePct"], how="left")["check"].isna())].drop_duplicates(["stateFips"])
US_results_states["trump"]=US_results_states.fullName=="Donald Trump"

#Keep max per countyFipsCode
temp=US_results.groupby("countyFips")["votePct"].max().reset_index()
temp["check"]=1


#Keep only winner
US_results=US_results[~(US_results.merge(temp, on=["countyFips","votePct"], how="left")["check"].isna())].drop_duplicates(["countyFips"])


US_results["countyFips"]=US_results["countyFips"].astype(str).str.zfill(5)

#Merge by State + County Name
df=df.merge(US_results, left_on=["countyFIPS","stateFIPS"], right_on=["countyFips","stateFips"], how="left")


df["trump"]=df.fullName=="Donald Trump"

with open("data/external/US/geojson-counties-fips.json") as response:
    counties = json.load(response)
    
print('Done')