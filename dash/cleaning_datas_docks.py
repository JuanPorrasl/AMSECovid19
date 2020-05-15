import pandas as pd
import numpy as np
import os
from datetime import datetime
import plotly.graph_objects as go

#Cases where the client does not have access to the links Cargo
try:
    from confidential.secrets import url_cargo, url_vessels
except:
    url_cargo=0
    url_vessels=0
    print("Cargos update links are not accessible. Did you set up the secrets.py file correctly? More information in the READ.ME")

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

ls=[path+"UpdateCargo",path+"UpdateVessels",path+"archives",path+"archives/HistoriqueMarchandises",path+"archives/HistoriqueNavires"]
for elem in ls:
    if(os.path.isdir(elem)==0):
        try:
            os.mkdir(elem)
        except OSError:
            print ("Creation of the directory failed")
            
#Create files to avoid bugs in HistoriqueNavires
if len(os.listdir(path+"archives/HistoriqueNavires"))==0:
    pd.DataFrame(data=[["03/01/2010 09:00","04/01/2010 04:00","HANJINAG - HANJIN","HANJINAG - HANJIN","ATP00014315","HNHL0049W","HNHL0049E","HANJIN HELSINKI","FOS","Validée","Validée"]], columns=["ARRIVEE","DEPART","Rep. Transp EM","Rep. Transp SM","id.AP+","Référence Arrivée","Référence Départ","Nom Navire","Bassin Touché","Statut Arrivée","Statut Départ"]).to_csv(path+'archives/HistoriqueNavires/AMU_VESSEL_2010.txt', sep='	', encoding = "ISO-8859-1")

## Update Cargo trafic
#Read files with "cargo" in title
folder="UpdateCargo/"
files=os.listdir(path+folder[:-1])

ls=[os.path.getmtime(path+folder+elem) for elem in files]

last_file=pd.to_datetime(files[ls.index(max(ls))][-10:-4], format='%d%m%y')
last_file_cargo=pd.to_datetime(files[ls.index(max(ls))][-10:-4], format='%d%m%y').strftime('%d/%m/%y')
today=pd.Timestamp.today()

#check if client can access to the links
if url_cargo != 0:
    #check time of precedent file
    if((last_file.year < today.year) | (last_file.week < (today.week-1))):
        try:
            cargo_update=pd.read_csv(url_cargo, encoding = "ISO-8859-1", sep=";")
            new_file=pd.to_datetime(cargo_update["Date fin"][1], format="%d/%m/%Y").strftime(folder[:-1]+'S%W%d%m%y.csv')
        except Exception as e:
            print("CARGOS EXCEPT ERROR: ******************************")
            print(e)
        else:
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

if url_vessels != 0:
    if((last_file.year < today.year) | (last_file.week < today.week)):
        try:
            cargo_update=pd.read_csv(url_vessels, encoding = "ISO-8859-1", sep=";")
            new_file=pd.Timestamp.today().strftime(folder[:-1]+'S%W%d%m%y.csv')
        except Exception as e:
            print("VESSELS EXCEPT ERROR: ******************************")
            print(e)
        else:
            #Save if not exist
            if new_file not in os.listdir(path+folder):
                #Remove previous file
                os.remove(path+folder+files[ls.index(max(ls))])
                #Save new file
                cargo_update.to_csv(path+folder+new_file, sep=";", encoding = "ISO-8859-1")

#Correction if file doesn't exist to force the condition IF == TRUE
if os.path.isfile(path+'../../processed/CARGO_2010-2020.xlsx'):
    datetime_cargos=datetime.fromtimestamp(os.path.getmtime(path+'../../processed/CARGO_2010-2020.xlsx')) 
else:
    datetime_cargos=datetime.fromtimestamp(1326244364)
    
## Update main file: Cargo

folder="UpdateCargo/"
## IF (Last Update file time > Main excel file time) => We update the main file
if datetime.fromtimestamp(max([os.path.getmtime(path+folder+elem) for elem in os.listdir(path+folder[:-1])])) > datetime_cargos:
    #Read previous file
    if os.path.isfile(path+'../../processed/CARGO_2010-2020.xlsx'):
        cargo=pd.read_excel(path+'../../processed/CARGO_2010-2020.xlsx', encoding = "ISO-8859-1", index_col=0).reset_index(drop=True)
    else:
        cargo=pd.DataFrame()
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
    
#Correction if file doesn't exist to force the condition IF == TRUE
if os.path.isfile(path+'../../processed/VESSEL_2010-2020.xlsx'):
    datetime_vessels=datetime.fromtimestamp(os.path.getmtime(path+'../../processed/VESSEL_2010-2020.xlsx'))
else:
    datetime_vessels=datetime.fromtimestamp(1326244364)
    
## Update main file: Vessels
folder="UpdateVessels/"
#If Update time > Main file time
if datetime.fromtimestamp(max([os.path.getmtime(path+folder+elem) for elem in os.listdir(path+folder[:-1])])) > datetime_vessels:
    #Read archives not CI5
    files=os.listdir(path+"archives/HistoriqueNavires")
    ls=[i for i in files if os.path.isfile(os.path.join(path+"archives/HistoriqueNavires",i)) and 'AMU' in i]
    
    #Read historical datas
    df=pd.DataFrame()
    for elem in ls:
        df_add=pd.read_csv(path+'archives/HistoriqueNavires/'+elem, sep="	", encoding = "ISO-8859-1")
        df=pd.concat([df,df_add])
    
    #Cleaning
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
    
    #Cleaning
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










