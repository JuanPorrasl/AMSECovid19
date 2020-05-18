#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 13:59:30 2020

@author: juanporras
"""
import pandas as pd
import numpy as np

import json
import urllib.request
from urllib.request import urlopen

import datetime
import time

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

#### BOGOTÁ CITY ####

#Downloading dataset
Covid_BOG = pd.read_csv("https://datosabiertos.bogota.gov.co/dataset/44eacdb7-a535-45ed-be03-16dbbea6f6da/resource/b64ba3c4-9e41-41b8-b3fd-2da21d627558/download/osb_enftransm-covid-19.csv"
                        ,sep=',',encoding='latin-1', error_bad_lines=False)
Covid_BOG['Cases'] = 1
Covid_BOG['Cumulative_Confirmed'] = Covid_BOG.groupby(['Fecha de diagnóstico','Localidad de residencia'])['Cases'].apply(lambda x: x.cumsum())

# Corrections

Estado_correct = {'Moderado ':'Moderado','Fallecido ':'Fallecido'}
Tipo_correct = {'En Estudio' : 'En estudio','Relacioando':'Relacionado','Relacionado ':'Relacionado',
                   'relacionado':'Relacionado','Importado ':'Importado','Desconocido ':'Desconocido',
                   'En estudio                                                                                                                                                                                              ': 'En estudio',
                   'En Estudio ':'En estudio'}
Ubic_correct = {'Casa                                                                                                                                                                                                    ':'Casa',
               'Hospital ':'Hospital'}
Estado_correct = {'Moderado                                                                                                                                                                                                    ':'Moderado',
                 'fallecido':'Fallecido'}

Covid_BOG['Sexo'] = Covid_BOG['Sexo'].replace({'f':'F'})
Covid_BOG['Tipo de caso'] = Covid_BOG['Tipo de caso'].replace(Tipo_correct)
Covid_BOG['Ubicación'] = Covid_BOG['Ubicación'].replace(Ubic_correct)
Covid_BOG['Estado'] = Covid_BOG['Estado'].replace(Estado_correct)

## English dictionary

#Values
Type_correct = {'Importado':'Imported',
                'Relacionado':'Related',
                'En estudio':'In Study',
                'Desconocido':'Unknown'}
Location_correct = {'Casa':'Home',
                    'Hospital UCI':'Intensive Care',
                    'Fallecido':'Death',
                    'Hospital':'Hospital',
                    'Recuperado':'Recovered'}
Health_cond_correct = {'Recuperado':'Recovered',
                       'Moderado':'Home',
                       'Crítico':'Hospital',
                       'Fallecido':'Death',
                       'Severo':'Intensive Care'} 

Covid_BOG['Tipo de caso'] = Covid_BOG['Tipo de caso'].replace(Type_correct)
Covid_BOG['Ubicación'] = Covid_BOG['Ubicación'].replace(Location_correct)
Covid_BOG['Estado'] = Covid_BOG['Estado'].replace(Health_cond_correct)

#Variables
new_columns = {'Fecha de diagnóstico':'Detection Date',
               'Ciudad de residencia':'City',
               'Localidad de residencia':'District',
               'Edad':'Age', 'Sexo':'Sex', 'Tipo de caso':'Origin Type',
               'Ubicación':'Treatment location','Estado':'State of treatment'}

Covid_BOG = Covid_BOG.rename(columns=new_columns)

#Bogotá Json file

url_bog="https://datosabiertos.bogota.gov.co/dataset/856cb657-8ca3-4ee8-857f-37211173b1f8/resource/497b8756-0927-4aee-8da9-ca4e32ca3a8a/download/loca.geojson"
with urlopen(url_bog) as response_bog:
    local_bog = json.load(response_bog)

for i in range(0,len(local_bog['features'])):
               local_bog['features'][i]['id'] = local_bog['features'][i]['properties']['LocNombre']

Localidades = []
for i in range(0,len(local_bog['features'])):
    local = local_bog['features'][i]['id']
    Localidades.append(local)

Covid_Localidad = pd.pivot_table(Covid_BOG, values='Cases', index='District',
                       columns=['State of treatment'], aggfunc=np.sum).reset_index()

Covid_Localidad['Total'] = Covid_Localidad[['Intensive Care', 'Death','Home','Recovered','Hospital']].sum(axis=1)
Covid_Localidad['Active'] = Covid_Localidad['Total'] - Covid_Localidad['Death'] - Covid_Localidad['Recovered']
Covid_Localidad = Covid_Localidad.fillna(0)
Covid_Localidad = Covid_Localidad.sort_values(by=['Active'],ascending= False).reset_index()
Covid_Localidad = Covid_Localidad.round()

Covid_Localidad['Fatality Rate'] = Covid_Localidad['Death']/Covid_Localidad['Total'] 

Localidad_dicc = {'SANTA FE':'Santa Fe',
 'PUENTE ARANDA':'Puente Aranda',
 'CIUDAD BOLIVAR':'Ciudad Bolívar',
 'BARRIOS UNIDOS':'Barrios Unidos',
 'SUBA':'Suba',
 'ANTONIO NARIÑO':'Antonio Nariño',
 'CANDELARIA':'La Candelaria',
 'ENGATIVA':'Engativá',
 'FONTIBON':'Fontibón',
 'SAN CRISTOBAL':'San Cristóbal',
 'TEUSAQUILLO':'Teusaquillo',
 'USAQUEN':'Usaquén',
 'CHAPINERO':'Chapinero',
 'USME':'Usme',
 'SUMAPAZ':'Sumapaz',
 'RAFAEL URIBE URIBE':'Rafael Uribe Uribe',
 'TUNJUELITO':'Tunjuelito',
 'LOS MARTIRES':'Los Mártires',
 'KENNEDY':'Kennedy',
 'BOSA':'Bosa'}

Localidad_dicc_r = dict(map(reversed, Localidad_dicc.items()))

Covid_Localidad['District'] = Covid_Localidad['District'].replace(Localidad_dicc_r)
Covid_Localidad['Recovery Rate'] = Covid_Localidad['Recovered']/Covid_Localidad['Total']

### Dataset for the map

Localidad_Map = Covid_Localidad
Localidad_Map

Localidad_Map['text'] = 'District: ' + Localidad_Map['District'].astype(str) + '<br>' + \
    'Active: ' + Localidad_Map['Active'].astype(str) + '<br>' + \
    'Deaths: ' + Localidad_Map['Death'].astype(str) + '<br>' + \
    'Recovered: ' + Localidad_Map['Recovered'].astype(str) + '<br>' + \
    'Hospitalization: ' + Localidad_Map['Hospital'].astype(str) + '<br>' + \
    'Intensive Care: ' + Localidad_Map['Intensive Care'].astype(str)


