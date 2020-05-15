#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 13:59:30 2020

@author: juanporras
"""
import pandas as pd
import numpy as np
import json

config = {'displayModeBar': False}

from cleaning_datas import df

#Data extracted from github
Condition = (df['Country_Region']== 'Colombia')
dfCOL = df[Condition]
dfCOL = dfCOL.sort_values('Last_Update')
dfCOL.reset_index()

dfCOL['ConfirmedGrowth'] =dfCOL.groupby('Country_Region')[['Confirmed']].pct_change()
dfCOL['DeathsGrowth'] =dfCOL.groupby('Country_Region')[['Deaths']].pct_change()
dfCOL['RecoveredGrowth'] =dfCOL.groupby('Country_Region')[['Recovered']].pct_change()

#Health National Institute

COL_Covid = pd.read_csv('https://www.datos.gov.co/api/views/gt2j-8ykr/rows.csv?accessType=DOWNLOAD')

new_columns = {'ID de caso':'Case_ID',
                  'Fecha de notificación':'Notification_date',
                  'Codigo DIVIPOLA':'DIVIPOLA_Code',
                  'Ciudad de ubicación':'City',
                  'Departamento o Distrito ':'Department',
                  'atención':'State_of_treatment',
                  'Edad':'Age',
                  'Sexo':'Sex',
                  'Tipo':'Origin_Type',
                  'Estado':'Health_condition',
                  'País de procedencia':'Country_of_Origin',
                  'FIS':'Symptoms_date',
                  'Fecha de muerte':'Death_date',
                  'Fecha diagnostico':'Detection_date',
                  'Fecha recuperado':'Date_of_Recovery',
                  'fecha reporte web':'Web_Reported_date'
                 }

COL_Covid = COL_Covid.rename(columns=new_columns)

#Correcting values
COL_Covid['Sex'] = COL_Covid['Sex'].replace({'m' : 'M','f':'F'})
COL_Covid['Origin_Type'] = COL_Covid['Origin_Type'].replace({'en estudio':'En estudio'})
COL_Covid['Health_condition'] = COL_Covid['Health_condition'].replace({'leve' : 'Leve'})
COL_Covid['Country_of_Origin'] = COL_Covid['Country_of_Origin'].replace({'COLOMBIANA' : 'Colombia'})

#New variables
COL_Covid['Notification_date'] = pd.to_datetime(COL_Covid['Notification_date']).dt.strftime('%Y/%m/%d')
COL_Covid['Symptoms_date'] = pd.to_datetime(COL_Covid['Symptoms_date'], errors='coerce').dt.strftime('%Y/%m/%d')
COL_Covid['Death_date'] = pd.to_datetime(COL_Covid['Death_date'], errors='coerce').dt.strftime('%Y/%m/%d')
COL_Covid['Detection_date'] = pd.to_datetime(COL_Covid['Detection_date']).dt.strftime('%Y/%m/%d')
COL_Covid['Date_of_Recovery'] = pd.to_datetime(COL_Covid['Date_of_Recovery'], errors='coerce').dt.strftime('%Y/%m/%d')
COL_Covid['Web_Reported_date'] = pd.to_datetime(COL_Covid['Web_Reported_date']).dt.strftime('%Y/%m/%d')

COL_Covid['Cases']=1
COL_Covid['Cumulative_Confirmed'] = COL_Covid.groupby(['Detection_date','City'])['Cases'].apply(lambda x: x.cumsum())

#Translation to english

State_treat_dicc = {'Recuperado':'Recovered', 'Casa':'Home', 'Fallecido':'Death',
                    'Hospital UCI':'Intensive Care', 'Hospital':'Hospitalization'}
Origin_dicc = {'Importado':'Imported', 'Relacionado':'Related', 'En estudio':'In study'}
Health_dicc = {'Leve':'Mild', 'Asintomático':'No Symptoms', 'Fallecido':'Death',
               'Grave':'Serious', 'Moderado':'Stable'}

COL_Covid['State_of_treatment'] = COL_Covid['State_of_treatment'].replace(State_treat_dicc)
COL_Covid['Origin_Type'] = COL_Covid['Origin_Type'].replace(Origin_dicc)
COL_Covid['Health_condition'] = COL_Covid['Health_condition'].replace(Health_dicc)

#DIVIPOLA CODES DANE
folder = "data"
DANE_Codes = pd.read_csv(folder+'/processed/DIVIPOLA_Col.csv').reset_index()
#Fixing columns
col_list = list(DANE_Codes)
col_list = col_list[1:]
col_list.append('Nan')
col_list
DANE_Codes.columns = col_list
DANE_Codes.drop(columns='Nan')
DANE_Codes['DIVIPOLA_Code'] = DANE_Codes['codigo_dpto_mpio']
DANE_Codes = DANE_Codes.drop(columns='codigo_dpto_mpio')
#Creating dicttionary
DANE = DANE_Codes.loc[:,['DIVIPOLA_Code','nombre_departamento']].drop_duplicates(subset=['DIVIPOLA_Code','nombre_departamento'])
#Mergin datasets
COL_Covid = pd.merge(COL_Covid, DANE, on=['DIVIPOLA_Code'],how='left')
COL_Covid = COL_Covid.rename(columns={'nombre_departamento':'Department_DANE'})
COL_Covid.dropna(subset=['Department_DANE'])

#By Cities

COL_City_Covid = pd.pivot_table(COL_Covid, values='Cases', index='City',
                       columns=['State_of_treatment'], aggfunc=np.sum)
COL_City_Covid['Total'] = COL_City_Covid[['Home', 'Death','Hospitalization','Intensive Care','Recovered']].sum(axis=1)
COL_City_Covid['Active'] = COL_City_Covid['Total'] - COL_City_Covid['Death'] - COL_City_Covid['Recovered']
COL_City_Covid = COL_City_Covid.fillna(0).reset_index()

#By Department

COL_Dep_Covid = pd.pivot_table(COL_Covid, values='Cases', index=['Department_DANE'],
                       columns=['State_of_treatment'], aggfunc=np.sum)
COL_Dep_Covid['Total'] = COL_Dep_Covid[['Home', 'Death','Hospitalization','Intensive Care','Recovered']].sum(axis=1)
COL_Dep_Covid['Active'] = COL_Dep_Covid['Total'] - COL_Dep_Covid['Death'] - COL_Dep_Covid['Recovered']
COL_Dep_Covid = COL_Dep_Covid.fillna(0).reset_index()
COL_Dep_Covid = COL_Dep_Covid.sort_values(by='Total',ascending=False)

today=COL_Covid['Detection_date']==pd.to_datetime(COL_Covid['Detection_date']).max().strftime("%m-%d-%Y")

#Load json file
with open("data/processed/colombia.geo.json") as response_co:
    states_co = json.load(response_co)
    
    
for i in range(0,len(states_co["features"])):
               states_co["features"][i]["id"] = states_co["features"][i]["properties"]["NOMBRE_DPT"]

#Cheking de set of departments of both datasets

Departments = []
for i in range(0,len(states_co["features"])):
    state = states_co["features"][i]["id"]
    Departments.append(state)
D1 = set(Departments)
D2 = set(COL_Dep_Covid['Department_DANE'].unique())
D2-D1


