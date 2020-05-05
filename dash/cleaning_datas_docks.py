import pandas as pd
import numpy as np
import os
from datetime import datetime
import plotly.graph_objects as go

from confidential.secrets import url_cargo, url_vessels

path="data/external/cargos/"
config = {'displayModeBar': False}

# Functions
def conversion(old):
    direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    new = old.replace(u'°',' ').replace('\'',' ').replace('"',' ')
    new = new.split()
    new_dir = new.pop()
    new.extend([0,0,0])
    return (int(new[0])+int(new[1])/60.0+int(new[2])/3600.0) * direction[new_dir]

####### First part : Update data

#Check folder exists
ls=[path+"UpdateCargo",path+"UpdateVessels"]
for elem in ls:
    if(os.path.isdir(elem)==0):
        try:
            os.mkdir(elem)
        except OSError:
            print ("Creation of the directory failed")
            
## Update Cargo trafic
#Read files with "cargo" in title
folder="UpdateCargo/"
files=os.listdir(path+folder[:-1])

ls=[os.path.getmtime(path+folder+elem) for elem in files]

last_file=pd.to_datetime(files[ls.index(max(ls))][-10:-4], format='%d%m%y')
last_file_cargo=pd.to_datetime(files[ls.index(max(ls))][-10:-4], format='%d%m%y').strftime('%d/%m/%y')
today=pd.Timestamp.today()

if((last_file.year < today.year) | (last_file.week < (today.week-1))):
    cargo_update=pd.read_csv(url_cargo, encoding = "ISO-8859-1", sep=";")
    new_file=pd.to_datetime(cargo_update["Date fin"][1]).strftime(folder[:-1]+'S%W%d%m%y.csv')
    #Save if not exist
    if new_file not in os.listdir(path+folder):
        cargo_update.to_csv(path+folder+new_file, sep=";", encoding = "ISO-8859-1")
        
## Update vessels trafic
folder="UpdateVessels/"
files=os.listdir(path+folder[:-1])

ls=[os.path.getmtime(path+folder+elem) for elem in files]

last_file=pd.to_datetime(files[ls.index(max(ls))][-10:-4], format='%d%m%y')
last_file_vessels=pd.to_datetime(files[ls.index(max(ls))][-10:-4], format='%d%m%y').strftime('%d/%m/%y')
today=pd.Timestamp.today()

if((last_file.year < today.year) | (last_file.week < (today.week-1))):
    cargo_update=pd.read_csv(url_vessels, encoding = "ISO-8859-1", sep=";")
    new_file=pd.Timestamp.today().strftime(folder[:-1]+'S%W%d%m%y.csv')
    #Save if not exist
    if new_file not in os.listdir(path+folder):
        #Remove previous file
        os.remove(path+folder+files[ls.index(max(ls))])
        #Save new file
        cargo_update.to_csv(path+folder+new_file, sep=";", encoding = "ISO-8859-1")


## Update main file: Cargo

folder="UpdateCargo/"
## IF (Last Update file time > Main excel file time) => We update the main file
if datetime.fromtimestamp(max([os.path.getmtime(path+folder+elem) for elem in os.listdir(path+folder[:-1])])) > datetime.fromtimestamp(os.path.getmtime(path+'../../processed/CARGO_2010-2020.xlsx')):
    #Read previous file
    cargo=pd.read_excel(path+'../../processed/CARGO_2010-2020.xlsx', encoding = "ISO-8859-1", index_col=0).reset_index(drop=True)
    #Read update files
    files=os.listdir(path+folder)
    ls=[i for i in os.listdir(path+folder)]
    #concat update files
    cargo_update=pd.DataFrame()
    for elem in ls:
        cargo_update_add=pd.read_csv(path+folder+elem, encoding = "ISO-8859-1", sep=";", index_col=0)
        cargo_update_add["date"]=pd.to_datetime(elem[-10:-4], format='%d%m%y')
        cargo_update=pd.concat([cargo_update_add,cargo_update])
    #Clean update files
    cargo_update.loc[cargo_update.Type=="IMPORT","Type"]=0
    cargo_update.loc[cargo_update.Type=="EXPORT","Type"]=1
    cargo_update=cargo_update.rename(columns={"Type":"export"})
    cargo_update=cargo_update[["Nom du port","export","Nb 20'","Nb 40'","Nb other","Nb roros","Roulant divers","Nb conv","date"]]

    cargo_update["somme"]=cargo_update[["Nb 20'", "Nb 40'", 'Nb other', 'Nb roros', 'Roulant divers', 'Nb conv']].sum(axis=1)
    cargo_update=cargo_update.reset_index(drop=True)

    cargo_update=pd.pivot_table(cargo_update, values='somme', index=['date','export'], columns=['Nom du port']).reset_index()
    cargo_update=cargo_update.rename(columns={"FRFOS":"FOS","FRMRS":"MRS"})
    #Concat both files
    cargo=pd.concat([cargo,cargo_update]).drop_duplicates(["date","export"])
    #If MRS & FOS are NA or ==0 -> Remove rows
    cargo=cargo[((~cargo["FOS"].isna()) & (~cargo["MRS"].isna())) | (~cargo["FOS"]==0) & (~cargo["MRS"]==0)]
    cargo=cargo.reset_index(drop=True)
    #Save
    cargo.to_excel(path+'../../processed/CARGO_2010-2020.xlsx', encoding = "ISO-8859-1")


## Update main file: Vessels
folder="UpdateVessels/"
#If Update time > Main file time
if datetime.fromtimestamp(max([os.path.getmtime(path+folder+elem) for elem in os.listdir(path+folder[:-1])])) > datetime.fromtimestamp(os.path.getmtime(path+'../../processed/VESSEL_2010-2020.xlsx')):
    #Read archives not CI5
    files=os.listdir(path+"archives/HistoriqueNavires")
    ls=[i for i in files if os.path.isfile(os.path.join(path+"archives/HistoriqueNavires",i)) and 'AMU' in i]

    df=pd.DataFrame()
    for elem in ls:
        df_add=pd.read_csv(path+'archives/HistoriqueNavires/'+elem, sep="	", encoding = "ISO-8859-1")
        df=pd.concat([df,df_add])

    df=df[["ARRIVEE","DEPART","Bassin Touché"]]
    df=df.rename(columns={"ARRIVEE":"cal_eta","DEPART":"cal_etd","Bassin Touché":"cal_place_code"})
    df.cal_eta=pd.to_datetime(df.cal_eta, format='%d/%m/%Y %H:%M')
    df.cal_etd=pd.to_datetime(df.cal_etd, format='%d/%m/%Y %H:%M')
    df=df[df.cal_place_code != "LIO"]

    df.cal_place_code=df.cal_place_code.replace("FOS","FRFOS")
    df.cal_place_code=df.cal_place_code.replace("MRS","FRMRS")

    #Read updates
    files=os.listdir(path+folder[:-1])
    vessels_update=pd.DataFrame()
    for elem in files:
        vessels_update_add=pd.read_csv(path+folder+elem, encoding = "ISO-8859-1", sep=";", index_col=0)
        vessels_update_add["date"]=pd.to_datetime(elem[-10:-4], format='%d%m%y')
        vessels_update=pd.concat([vessels_update_add,vessels_update])

    vessels_update=vessels_update[["cal_eta","cal_etd","cal_place_code","cal_last_place_code","cal_next_place_code"]]
    vessels_update=vessels_update[(vessels_update.cal_place_code=="FRFOS") | (vessels_update.cal_place_code=="FRMRS")]

    #Concat
    df=pd.concat([df,vessels_update])
    df=df.reset_index(drop=True)

    df.cal_etd=df.cal_etd.replace("<null>","")
    df.cal_eta=df.cal_eta.replace("<null>","")
    df.cal_last_place_code=df.cal_last_place_code.replace("<null>",float("NaN"))
    df.cal_next_place_code=df.cal_next_place_code.replace("<null>",float("NaN"))
    df.cal_eta=pd.to_datetime(df.cal_eta)
    df.cal_etd=pd.to_datetime(df.cal_etd)
    df["cal_diff"]=(df.cal_etd-df.cal_eta)/np.timedelta64(1,'D')
    df=df.drop_duplicates()
    
    #Save file
    df.to_excel(path+"../../processed/VESSEL_2010-2020.xlsx")
    #Get free RAM
    del(df, vessels_update, vessels_update_add, df_add)


####### Second part : Cleaning datas
#Read cargo file
cargo=pd.read_excel(path+"../../processed/CARGO_2010-2020.xlsx", encoding = "ISO-8859-1", index_col=0)
#Read vessels files
vessels=pd.read_excel(path+"../../processed/VESSEL_2010-2020.xlsx", encoding = "ISO-8859-1", index_col=0)
#Read seacode
seacode=pd.read_csv(path+"../../processed/seaport_code.csv", index_col=0)

# Cleaning vessels
vessels["counter"]=1
vessels.loc[:,"date"]=vessels.cal_eta.dt.to_period('M').dt.to_timestamp()

# Cleaning cargo
cargo=cargo[["MRS","FOS","export","date"]]
cargo=cargo.sort_values("date")
cargo.loc[:,"MRS"]=cargo.loc[:,"MRS"].astype(float)
cargo.loc[:,"FOS"]=cargo.loc[:,"FOS"].astype(float)
cargo=cargo[(~cargo.MRS.isna()) & (~cargo.FOS.isna()) & ((cargo.MRS!=0) & (cargo.FOS!=0))]
#Floor to month
cargo.date=cargo.date.dt.to_period('M').dt.to_timestamp()


#Badges last updates










