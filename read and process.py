import pandas as pd
import numpy as np
# PSUs nested within Strata accounts for the design effects*  NEST SDMVSTRA SDMVPSU / MISSUNIT;
#* Weight statement: specify appropriate weight, accounts for the unequal probability of sampling and non-response.*;
# WEIGHT wtint2yr;
  
from samplics.weighting import SampleWeight
# downside of NHANES is that it has got a small sample size and would not cover speciality medications eg cancer, immune etc
dfdemog=pd.read_xml(r"C:\Users\manas\Dropbox\HP_Desktop\D Drive\Data\Oasis_scan\NHANES\NHANES 2017-March 2020 Pre-pandemic Demographics.xml")
#                    "C:\Users\manas\Dropbox\HP_Desktop\D Drive\Data\Oasis_scan\NHANES\NHANES 2017-2018 Demographics.csv")
dfdemog.columns
basiclist=['SEQN','SDDSRVYR','RIDSTATR','RIAGENDR','RIDAGEYR']
for x in basiclist:
    dfdemog[x]=dfdemog[x].astype(int)
dfdemog['RIDAGEMN']=dfdemog['RIDAGEMN'].astype('float16')
#remove the rows which are all duplicates of the last data row
dfdemog=dfdemog[dfdemog['SEQN']!=0]
dfdemog=dfdemog.drop_duplicates(subset=['SEQN'],keep='first')
dfdemog=dfdemog[['SEQN','WTINTPRP','WTMECPRP','SDMVPSU', 'SDMVSTRA']]

print(dfdemog['WTMECPRP'])

NHANES_med_file=r"C:\Users\manas\Dropbox\HP_Desktop\D Drive\Data\Oasis_scan\NHANES\NHANES 2017-March 2020 Pre-pandemic Prescription Medications.xml"
#"C:\Users\manas\Dropbox\HP_Desktop\D Drive\Data\Oasis_scan\NHANES\2017-March 2020 NHANES Prescription Medications.csv"
dfmed = pd.read_xml(NHANES_med_file)
basiclist=['SEQN','RXDUSE']
for x in basiclist:
    dfmed[x]=dfmed[x].astype(int)
#remove the rows which are all duplicates of the last data row
dfmed=dfmed[dfmed['SEQN']!=0]
dfmed=dfmed[['SEQN','RXDDRUG']]
dfmedd=dfmed.groupby(['SEQN']).count().to_dict()['RXDDRUG']

# make  meds that are numbers as nan
re2 = '\d.*'
dfmed['RXDDRUG']=np.where(dfmed['RXDDRUG'].str.match(re2),np.NAN, dfmed['RXDDRUG'].str.lower())

# following are somewhat convuluted steps to make long data wide

for index in range(len(dfmed)):
    if dfmed.at[index, 'SEQN'] in dfmedd.keys():
        dfmed.at[index, 'vaz']=dfmedd[dfmed.at[index, 'SEQN']]
dfmed['vaz']=dfmed['vaz'].astype(int)
dfmed=dfmed.dropna(subset=['SEQN'])

dfmedl=dfmed.drop_duplicates(subset=['SEQN'],keep='first')
dfmedl=dfmedl.reset_index()
dfmedl.columns
dfmedl.rename(columns={"index": "atom"},inplace=True)
dfmedlist=dfmedl['atom'].to_list()
dfmed[dfmed['SEQN']==124821]
dfmed[dfmed['SEQN']==124822]


for index in dfmedlist:
    for x in range(dfmed.at[index, 'vaz']):
        dfmed.at[index+x, 'itemz']="med"+str(x)
       
dfmed[dfmed['SEQN']==124821]

dfmed=dfmed.dropna(subset=['SEQN'])
dfmed['SEQN']=dfmed['SEQN'].astype(int)
#dfmed=dfmed.sort_values(by=['itemz'])   
dfmed['itemz']= np.where(dfmed['itemz'].isna(), "",dfmed['itemz'] )
dfmed['RXDDRUG']= np.where(dfmed['RXDDRUG'].isna(), "",dfmed['RXDDRUG'] )
dfmed=dfmed[['SEQN','RXDDRUG','itemz']]
dfmedw=dfmed.pivot(index='SEQN', columns='itemz', values='RXDDRUG')
dfmedw=dfmedw.reset_index()
dfmedw.info()
dfmedw['SEQN']
#merge demographic data, weights with medications
dfdemog['SEQN']
dfdemog=dfdemog.sort_values(by=['SEQN'])   
dfmedw=dfmedw.sort_values(by=['SEQN'])   

df= dfdemog.merge(dfmedw, left_on='SEQN', right_on='SEQN')

df