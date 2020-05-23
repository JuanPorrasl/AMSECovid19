###################################
########## General Datas ##########
###################################

import os
#os.chdir("D:/Utilisateur/Documents/Documents/Cours/AMSE M2 S4/COVID19")

import pandas as pd
import numpy as np
import urllib.request
import datetime
import time
from datetime import datetime

def timer():
    return '['+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+']'

url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'
folder = "data"

pd.set_option('display.max_columns', 20)
config = {'displayModeBar': False}

############# CLEANING PART #############
#Create /datas folder if it not exists
if(os.path.isdir(folder)==0):
    try:
        os.mkdir(folder)
    except OSError:
        print ("Creation of the directory failed")
        
if(os.path.isdir(folder+"/external/hopkins")==0):
    try:
        os.mkdir(folder+"/external/hopkins")
    except OSError:
        print ("Creation of the directory failed")

#Date of first file
start=pd.Timestamp("2020-01-22").strftime("%m-%d-%Y")

#If folder empty, download first file
if(len(os.listdir(folder+"/external/hopkins")) == 0):
    file=url+start+".csv"
    urllib.request.urlretrieve(file, folder+"/external/hopkins/"+start+".csv")
    
list_files=os.listdir(folder+"/external/hopkins")

#Remove extension
list_files=[sub[ : -4] for sub in list_files] 

#Start
start=pd.Timestamp("2020-01-22")
#Now
end=pd.Timestamp.today()

#Difference in days
delta=(end-start).days

#Foreach day, check if file is in dir. Else: download it.
print (timer()+'[INFO] Checking Hopkins updates...')
for i in range(1,delta+1):
    day=str((start+pd.Timedelta(str(i)+" days")).strftime("%m-%d-%Y"))
    
    #If False: download file. With sleep of 1 second everytime
    if(os.path.isfile(folder+"/external/hopkins/"+day+".csv"))==0:
        file=url+day+".csv"
        try:
            urllib.request.urlretrieve(file, folder+"/external/hopkins/"+day+".csv")
        except OSError:
            print (timer()+'[INFO] '+day+'.csv not available')
        else:
            print (timer()+'[INFO] '+day+'.csv downloaded')
            time.sleep(1)

#Load all files
list_files=os.listdir(folder+"/external/hopkins")
list_files.sort()

days=pd.DataFrame()

#Loading datas
for elem in list_files[0:11]:
    new_day = pd.read_csv(folder+"/external/hopkins/"+elem, parse_dates=[0], sep=",")
    #I'm correcting the date here because the authors changed the date format 4 times.
    new_day["Last Update"]=elem[:-4]
    days = pd.concat([new_day, days], sort=True)
#Correction of columns names
days=days.rename(columns={"Country/Region": "Country_Region", "Last Update": "Last_Update", "Province/State": "Province_State"})

days2=pd.DataFrame()

#Loading datas
for elem in list_files[11:60]:
    new_day = pd.read_csv(folder+"/external/hopkins/"+elem, parse_dates=[0], sep=",")
    #I'm correcting the date here because the authors changed the date format 4 times.
    new_day["Last Update"]=elem[:-4]
    days2 = pd.concat([new_day, days2], sort=True)

days2=days2.rename(columns={"Country/Region": "Country_Region", "Last Update": "Last_Update","Latitude": "Lat","Longitude": "Long_", "Province/State": "Province_State"})
days3=pd.DataFrame()

#Loading datas
for elem in list_files[60:]:
    new_day = pd.read_csv(folder+"/external/hopkins/"+elem, parse_dates=[0], sep=",")
    #I'm correcting the date here because the authors changed the date format 4 times.
    new_day["Last_Update"]=elem[:-4]
    days3 = pd.concat([new_day, days3], sort=True)

#Fusion
df=pd.concat([days3, days2, days], sort=True)

#Remove days for space
del(days, days2, days3)

#Remove useless columns
df=df.drop(["Admin2", "Combined_Key", "FIPS"], axis=1)

#Dealing with exceptions
df.loc[df["Country_Region"]=="Mainland China","Country_Region"]="China"

#Remove row when there is no time
df=df[df["Last_Update"]!=0]

#When no location -> NaN
df.loc[df["Lat"]==0,"Lat"]=float("NaN")
df.loc[df["Long_"]==0,"Long_"]=float("NaN")

df.Last_Update=pd.to_datetime(df.Last_Update, format='%m-%d-%Y')

continent=pd.read_excel(folder+'/processed/country2continent.xlsx', index_col=0)
df=df.merge(continent, left_on='Country_Region', how='left', right_on='Country_Region')

#Remove country if number of observations < 20 (create bugs)
temp=df.groupby("Country_Region", as_index=False)["Lat"].agg(["count"])["count"].reset_index()
keep_country=temp.loc[(temp["count"] > 20),"Country_Region"]
df=df[df.Country_Region.isin(keep_country)]
del(temp, keep_country)


#Add groupby date for sum Worldwide datas
temp=pd.DataFrame(df.groupby("Last_Update", as_index=False)[["Active","Confirmed","Deaths","Recovered"]].sum())
temp["Country_Region"]="Worldwide"
temp["Lat"], temp["Long_"], temp["Province_State"] = float("NaN"), float("NaN"), float("NaN")

temp=temp.reset_index(drop=True)
df=pd.concat([temp, df])
del(temp)


last_file_hopkins=df['Last_Update'].max().strftime('%d/%m/%y')

today=list(df['Last_Update']==df['Last_Update'].max())
yesterday=list(df['Last_Update']==(df['Last_Update']-pd.Timedelta(days=1)).max())

# Group US and sort by Active cases
df_today=df.loc[today,:].groupby(["Country_Region"]).sum().loc[:,["Active","Confirmed","Deaths","Recovered"]].sort_values(by=['Active'],ascending= False).reset_index()

# POPULATION DATA
pop=pd.read_csv(folder+'/processed/Population.csv', index_col=False)

#Drop some variables and keep only this year
pop_today = pop[pop['Time']==pd.Timestamp.today().year].reset_index().drop(columns= ['index','LocID','Variant','VarID','MidPeriod'])
#Convert to millions
pop_today[['PopMale','PopFemale','PopTotal']] = pop_today[['PopMale','PopFemale','PopTotal']].multiply(1000, axis="index")

UN_dict = {
    'Bolivia (Plurinational State of)': 'Bolivia',
    'Brunei Darussalam': 'Brunei',
    'Myanmar': 'Burma',
    'Congo':'Congo (Brazzaville)',
    'Democratic Republic of the Congo':'Congo (Kinshasa)',
    "Côte d'Ivoire":"Cote d'Ivoire",
    'Iran (Islamic Republic of)':'Iran',
    'Republic of Korea':'Korea, South',
    "Lao People's Democratic Republic":'Laos',
    'Republic of Moldova':'Moldova',
    'Russian Federation':'Russia',
    'Syrian Arab Republic':'Syria',
    'United Republic of Tanzania':'Tanzania',
    'United States of America':'US',
    'Venezuela (Bolivarian Republic of)':'Venezuela',
    'Viet Nam':'Vietnam',   
}

pop_today['Location'] = pop_today['Location'].replace(UN_dict)

df_pop = df_today.merge(pop_today, left_on = 'Country_Region', right_on = 'Location').drop(columns= ['Location','Time']) 
del(df_today)
df_pop['Lethality'] = (df_pop['Deaths']/df_pop['Confirmed'])*100
df_pop['Confirmed/Pop'] = (df_pop['Confirmed']/df_pop['PopTotal'])*100
df_pop['Active/Pop'] = (df_pop['Active']/df_pop['PopTotal'])*100
df_pop['Recovered/Pop'] = (df_pop['Recovered']/df_pop['PopTotal'])*100
df_pop['Deaths/Pop'] = (df_pop['Deaths']/df_pop['PopTotal'])*100
