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

from datetime import datetime
import time

def timer():
    return '['+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+']'

config = {'displayModeBar': False}
folder = "data/"
from cleaning_datas import df

print(timer()+"[INFO] Loading colombia page")
#Data extracted from github
Condition = (df['Country_Region']== 'Colombia')
dfCOL = df[Condition]
dfCOL = dfCOL.sort_values('Last_Update').reset_index()

dfCOL['ConfirmedGrowth'] =dfCOL.groupby('Country_Region')[['Confirmed']].pct_change()
dfCOL['DeathsGrowth'] =dfCOL.groupby('Country_Region')[['Deaths']].pct_change()
dfCOL['RecoveredGrowth'] =dfCOL.groupby('Country_Region')[['Recovered']].pct_change()

#Health National Institute datas
#We do a copy in case loading data fail
try:
    COL_Covid = pd.read_csv('https://www.datos.gov.co/api/views/gt2j-8ykr/rows.csv?accessType=DOWNLOAD')
    #Save in our repertory
    COL_Covid.to_csv(folder+"external/colombia/Casos_positivos_de_COVID-19_en_Colombia.csv")
except Exception as e:
    #If fail, we load our file
    print('\033[1;31;48m'+timer()+'[WARNING] Colombia COL_Covid link is not accessible. Reading previous file..')
    COL_Covid = pd.read_csv(folder+"external/colombia/Casos_positivos_de_COVID-19_en_Colombia.csv")
    
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

#Correcting uppercases
for elem in ["Origin_Type", "Health_condition", "Country_of_Origin", "Sex"]:
    COL_Covid[elem]=COL_Covid[elem].str.capitalize()

#Correcting values when "- -" then NA
#Then save
for elem in ["Notification_date","Symptoms_date","Death_date","Detection_date","Date_of_Recovery", "Web_Reported_date"]:
    COL_Covid.loc[COL_Covid[elem]=="-   -",elem]=float("NaN")
    COL_Covid[elem] = pd.to_datetime(COL_Covid[elem], errors='coerce').dt.strftime('%Y/%m/%d')

COL_Covid['Cases']=1
COL_Covid['Cumulative_Confirmed'] = COL_Covid.groupby(['Detection_date','City'])['Cases'].agg(["cumsum"])

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
DANE_Codes = pd.read_csv(folder+'/processed/DIVIPOLA_Col.csv').reset_index(drop=True)

#Fix columns
DANE_Codes.columns=DANE_Codes.columns[1:].tolist()+["NaN"]
DANE_Codes.drop(columns='NaN')

#Rename columns
DANE_Codes = DANE_Codes.rename(columns={"codigo_dpto_mpio":"DIVIPOLA_Code"})

#Creating dictionary
DANE_Codes = DANE_Codes.loc[:,['DIVIPOLA_Code','nombre_departamento']].drop_duplicates(subset=['DIVIPOLA_Code','nombre_departamento'])

#Mergin datasets
COL_Covid = pd.merge(COL_Covid, DANE_Codes, on=['DIVIPOLA_Code'],how='left')
#Free space
del(DANE_Codes)
COL_Covid = COL_Covid.rename(columns={'nombre_departamento':'Department_DANE'})
COL_Covid.dropna(subset=['Department_DANE'])


#Function : do pivot for a df given (df must be COL_Covid format)
def by_colombia(df,index, cols):
    df = pd.pivot_table(df, values='Cases', index=index, columns=['State_of_treatment'], aggfunc=np.sum)
    df['Total'] = df[cols].sum(axis=1)
    df['Active'] = df['Total'] - df['Death'] - df['Recovered']
    df = df.fillna(0).reset_index()
    df = df.sort_values(by='Total',ascending=False)
    return df

#By Cities
COL_City_Covid=by_colombia(COL_Covid,"City",['Home', 'Death','Hospitalization','Intensive Care','Recovered'])
#By Department
COL_Dep_Covid=by_colombia(COL_Covid,"Department_DANE",['Home', 'Death','Hospitalization','Intensive Care','Recovered'])

today=COL_Covid['Detection_date']==pd.to_datetime(COL_Covid['Detection_date']).max().strftime('%Y/%m/%d')

#Load json file
with open(folder+"processed/colombia.geo.json") as response_co:
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


#### BOGOTÁ CITY ####
print(timer()+"[INFO] Loading bogota city")
#Downloading dataset
try:
    Covid_BOG = pd.read_csv("https://datosabiertos.bogota.gov.co/dataset/44eacdb7-a535-45ed-be03-16dbbea6f6da/resource/b64ba3c4-9e41-41b8-b3fd-2da21d627558/download/osb_enftransm-covid-19.csv"
                        ,sep=',',encoding='latin-1', error_bad_lines=False, warn_bad_lines=False)
    #Save in our repertory
    Covid_BOG.to_csv(folder+"external/colombia/osb_enftransm-covid-19.csv", sep=',',encoding='latin-1')
except Exception:
    #If fail, we load our file
    print('\033[1;31;48m'+timer()+'[WARNING] Bogota link is not accessible. Reading previous file..')
    Covid_BOG = pd.read_csv(folder+"external/colombia/osb_enftransm-covid-19.csv", sep=',',encoding='latin-1', error_bad_lines=False, warn_bad_lines=False)
 
Covid_BOG['Cases'] = 1
Covid_BOG['Cumulative_Confirmed'] = Covid_BOG.groupby(['Fecha de diagnóstico','Localidad de residencia'])['Cases'].agg(["cumsum"])

# Corrections strip and capitalize
for elem in ["Sexo","Tipo de caso","Ubicación","Estado"]:
    Covid_BOG[elem]=Covid_BOG[elem].str.strip()
    Covid_BOG[elem]=Covid_BOG[elem].str.capitalize()

#Convert to english
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
with open(folder+"processed/bogota.geojson") as response_bog:
    local_bog = json.load(response_bog)

for i in range(0,len(local_bog['features'])):
               local_bog['features'][i]['id'] = local_bog['features'][i]['properties']['LocNombre']

Localidades = []
for i in range(0,len(local_bog['features'])):
    local = local_bog['features'][i]['id']
    Localidades.append(local)

#By Cities
Covid_BOG=Covid_BOG.rename(columns={"State of treatment":"State_of_treatment"})
Covid_Localidad=by_colombia(Covid_BOG,"District", ['Intensive Care', 'Death','Home','Recovered','Hospital'])
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

