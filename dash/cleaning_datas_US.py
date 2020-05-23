#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 11:49:28 2020

@author: juanporras
"""

import pandas as pd
import numpy as np

import json
import urllib.request
from urllib.request import urlopen

config = {'displayModeBar': False}

from cleaning_datas import df

df_US=df[(df["Country_Region"]=="US")]
df_US = df_US.groupby(['Last_Update', 'Country_Region','Province_State']).sum().loc[:,['Confirmed','Recovered','Deaths']].reset_index()
df_US["Last_Update"] = pd.to_datetime(df_US["Last_Update"]).dt.strftime('%m/%d/%Y')

Raw_Capital_dict = {
    'Alabama': 'Montgomery',
    'Alaska': 'Juneau',
    'Arizona':'Phoenix',
    'Arkansas':'Little Rock',
    'California': 'Sacramento',
    'Colorado':'Denver',
    'Connecticut':'Hartford',
    'Delaware':'Dover',
    'Florida': 'Tallahassee',
    'Georgia': 'Atlanta',
    'Hawaii': 'Honolulu',
    'Idaho': 'Boise',
    'Illinios': 'Springfield',
    'Indiana': 'Indianapolis',
    'Iowa': 'Des Monies',
    'Kansas': 'Topeka',
    'Kentucky': 'Frankfort',
    'Louisiana': 'Baton Rouge',
    'Maine': 'Augusta',
    'Maryland': 'Annapolis',
    'Massachusetts': 'Boston',
    'Michigan': 'Lansing',
    'Minnesota': 'St. Paul',
    'Mississippi': 'Jackson',
    'Missouri': 'Jefferson City',
    'Montana': 'Helena',
    'Nebraska': 'Lincoln',
    'Neveda': 'Carson City',
    'New Hampshire': 'Concord',
    'New Jersey': 'Trenton',
    'New Mexico': 'Santa Fe',
    'New York': 'Albany',
    'North Carolina': 'Raleigh',
    'North Dakota': 'Bismarck',
    'Ohio': 'Columbus',
    'Oklahoma': 'Oklahoma City',
    'Oregon': 'Salem',
    'Pennsylvania': 'Harrisburg',
    'Rhoda Island': 'Providence',
    'South Carolina': 'Columbia',
    'South Dakoda': 'Pierre',
    'Tennessee': 'Nashville',
    'Texas': 'Austin',
    'Utah': 'Salt Lake City',
    'Vermont': 'Montpelier',
    'Virginia': 'Richmond',
    'Washington': 'Olympia',
    'West Virginia': 'Charleston',
    'Wisconsin': 'Madison',
    'Wyoming': 'Cheyenne'  
}

Capital_dict = dict(map(reversed, Raw_Capital_dict.items()))

df_US['State'] = df_US['Province_State'].replace(Capital_dict)

State_dict = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

State_inverse_dict = dict(map(reversed, State_dict.items()))

list_us=df_US.loc[df_US["Country_Region"]=="US","State"].reset_index(drop=True)
for elem in range(0,len(list_us)):
    if len(list_us[elem].split(", ",1))==2:
        list_us[elem]=list_us[elem].split(", ",1)[1].replace(".","")[0:2]
        if list_us[elem]=="US":
            list_us[elem]=float("NaN")
    else:
        if list_us[elem].split(", ",1)[0] in State_dict:
            list_us[elem]=State_dict[list_us[elem].split(", ",1)[0]]
        else:
            if list_us[elem].split(", ",1)[0]=="Chicago":
                list_us[elem]="IL"
            else:
                list_us[elem]=float("NaN")

df_US['State_Code'] = list_us

### Load Json File

url_us="https://raw.githubusercontent.com/jgoodall/us-maps/master/geojson/state.geo.json"
with urlopen(url_us) as response_us:
    states_us = json.load(response_us)

for i in range(0,len(states_us["features"])):
               states_us["features"][i]["id"] = states_us["features"][i]["properties"]["STUSPS10"]

States = []
for i in range(0,len(states_us["features"])):
    state = states_us["features"][i]["id"]
    States.append(state)
    
S1 = set(States)
S2 = set(df_US['State_Code'].unique())
S2-S1

# Center for Disease Control and Prevention

# Provisional Covid19 Death Count by week, ending date and state (Deaths)

deaths = pd.read_csv("https://data.cdc.gov/api/views/r8kw-7aab/rows.csv?accessType=DOWNLOAD")

# Race and Hispanic Origin (Deaths)

Demographic = pd.read_csv("https://data.cdc.gov/api/views/pj7m-y5uh/rows.csv?accessType=DOWNLOAD")
Demographic['State Name'] = Demographic['State'].replace(State_inverse_dict)

# Three Different Datasets

cond1 = (Demographic['Indicator']=='Distribution of COVID-19 deaths (%)')
cond2 = (Demographic['Indicator']=='Weighted distribution of population (%)')
cond3 = (Demographic['Indicator']=='Unweighted distribution of population (%)')
Deaths_Covid = Demographic[cond1].drop(columns=['Indicator','Footnote'])
Weighted_pop = Demographic[cond2]
Unweighted_pop = Demographic[cond3]

# Tests DATASET

Current_State = pd.read_csv('https://covidtracking.com/api/v1/states/current.csv')
Current_State['state_name'] = Current_State['state'].replace(State_inverse_dict)


