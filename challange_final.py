"""
Title: Data Incubator challange questions
Author: Saman Monjezi
Submited to: Data Incubator
Date: 10/28/2018
"""
for name in dir(): # remove old variables
    if not name.startswith('_'):
        del globals()[name]
import os
import csv
from datetime import datetime
import numpy as np
import math
import pandas as pd
import array as arr
import congress
from congress import Congress
def lookup(s):#fast str to date convesion
    dates = {date:pd.to_datetime(date, errors='coerce') for date in s.unique()}
    return s.map(dates)
file_dir='C:/Users/SamDesk/Desktop/Challenge/data1/' #files path
mylist = os.listdir(file_dir)
#total_pay = 0
index1=0
#expend_since_2016=0
avg_ann_exp=[0 for i in range(7)]
array_turnover=[0 for i in range(6)]
for filename in mylist:
    print('loading  ',filename)
    index1 +=1
    df= pd.read_csv(file_dir+filename,encoding = "ISO-8859-1")
    df_Q=df[['BIOGUIDE_ID','OFFICE','CATEGORY','PAYEE','START DATE','END DATE','PURPOSE','AMOUNT']]
    if index1==1:
        df_all=df_Q
    else:
        df_all=pd.concat([df_all,df_Q], ignore_index=True)
print('data loaded ...')
df_all['AMOUNT']=df_all['AMOUNT'].astype(str).str.replace(',', '').convert_objects(convert_numeric=True) # remove "," between numbers, convert to float
df_all['START DATE']=lookup(df_all['START DATE'])
df_all['END DATE']=lookup(df_all['END DATE'])

#Q1
total_expenditure = df_all['AMOUNT'].sum()
print('Q1 - total expenditure:  $',total_expenditure,sep="")


#Q2
coverage_period_Q2=(df_all['END DATE']-df_all['START DATE'])[(df_all['AMOUNT']>0) & (df_all['START DATE'].notnull())] # only positive amounts & avaiable dates
coverage_period_Q2=coverage_period_Q2.dt.total_seconds()/ (24 * 3600)
coverage_period_Q2_std=coverage_period_Q2.std(ddof=1)
print('Q2 - standard deviation of the coverage period:  ',coverage_period_Q2_std, ' Days')

#Q3
for i in range(2010 , 2017):
    avg_ann_exp[i-2010]=df_all['AMOUNT'][(df_all['AMOUNT']>0) & (df_all['START DATE'].dt.year==i)].sum()
print("Q3 - average annual expenditure (2010 - 2016):  $",np.mean(avg_ann_exp),sep="")

#Q4
expenditure_2016=df_all['AMOUNT'][(df_all['START DATE'].dt.year==2016)].sum()
df_2016=df_all[['OFFICE','PURPOSE','AMOUNT']][(df_all['START DATE'].dt.year==2016)]
pivot_2016_office=pd.pivot_table(df_2016,index=["OFFICE"],values = 'AMOUNT',aggfunc=np.sum).sort_values(by='AMOUNT', ascending=False, na_position='first')
name_top_office=pivot_2016_office.index.get_level_values('OFFICE')[0]
df_top_office=df_2016[df_2016['OFFICE'].isin([name_top_office])]
pivot_2016_purpose=pd.pivot_table(df_top_office,index=["PURPOSE"],values = 'AMOUNT',aggfunc=np.sum).sort_values(by='AMOUNT', ascending=False, na_position='first')
purpose_percnt=pivot_2016_purpose['AMOUNT'][0]/expenditure_2016
print('Q4 - the ratio of top porpose of top office to total expenditure in 2016:  ',purpose_percnt,sep="")

#Q5
df_2016=df_all[['BIOGUIDE_ID','PAYEE','AMOUNT']][(df_all['START DATE'].dt.year==2016) & (df_all['BIOGUIDE_ID'].notna()) & (df_all['CATEGORY'].str.contains("PERSONNEL COMPENSATION"))]
df_2016['PAYEE']=df_2016['PAYEE'].str.replace('.','') #make names consistent
df_2016['PAYEE']=df_2016['PAYEE'].str.strip()
df_2016['PAYEE']=df_2016['PAYEE'].str.replace(',',' ')
df_2016['PAYEE']=df_2016['PAYEE'].str.replace('  ',' ')
df_staff_count=df_2016.reset_index().groupby('BIOGUIDE_ID')['PAYEE'].nunique()
pivot_2016_staff=pd.pivot_table(df_2016,index=["BIOGUIDE_ID"],values = 'AMOUNT',aggfunc=np.sum)
average_salary_max_2016=(pivot_2016_staff['AMOUNT']/df_staff_count).reset_index()[0].max()
print('Q5 - maximum average salary in 2016:  $',average_salary_max_2016,sep="")

#Q6
df_turnover_old=df_all[['BIOGUIDE_ID','PAYEE']][(df_all['START DATE'].dt.year==2010) & (df_all['BIOGUIDE_ID'].notna()) & (df_all['CATEGORY'].str.contains("PERSONNEL COMPENSATION"))]
df_turnover_old['PAYEE']=df_turnover_old['PAYEE'].str.replace('.','') #make names consistent
df_turnover_old['PAYEE']=df_turnover_old['PAYEE'].str.strip()
df_turnover_old['PAYEE']=df_turnover_old['PAYEE'].str.replace(',',' ')
df_turnover_old['PAYEE']=df_turnover_old['PAYEE'].str.replace('  ',' ')
df_turnover_old=df_turnover_old.drop_duplicates(keep="first")
df_turnover_old.set_index('BIOGUIDE_ID', inplace=True)
df_rep_data=df_turnover_old.reset_index()['BIOGUIDE_ID'].drop_duplicates(keep="first").reset_index().drop(['index'], axis=1) #get ID of current reps
df_rep_data['YEAR JOINED']=pd.DataFrame(np.asarray([2010 for i in range(0,len(df_rep_data.reset_index()['BIOGUIDE_ID']))]), index=df_rep_data.reset_index()['BIOGUIDE_ID'].index)
df_rep_data['YEAR LEFT']=pd.DataFrame(np.asarray([2017 for i in range(0,len(df_rep_data.reset_index()['BIOGUIDE_ID']))]), index=df_rep_data.reset_index()['BIOGUIDE_ID'].index)
df_rep_data['2010 TURNOVER']=pd.DataFrame(np.asarray([np.NaN for i in range(0,len(df_rep_data['BIOGUIDE_ID']))]), index=df_rep_data['BIOGUIDE_ID'].index)
df_rep_data.set_index('BIOGUIDE_ID', inplace=True)
df_rep_data['2010 STAFF SIZE']=df_turnover_old.reset_index().groupby('BIOGUIDE_ID')['PAYEE'].nunique()
list_rep_ID_old=df_rep_data.reset_index()['BIOGUIDE_ID'].tolist()
for i in range(2011 , 2017):
    df_rep_data[str(i)+' TURNOVER']=np.NaN
    df_rep_data[str(i)+' STAFF SIZE']=np.NaN
    df_turnover_new=df_all[['BIOGUIDE_ID','PAYEE']][(df_all['START DATE'].dt.year==i) & (df_all['BIOGUIDE_ID'].notna()) & (df_all['CATEGORY'].str.contains("PERSONNEL COMPENSATION"))]
    df_turnover_new['PAYEE']=df_turnover_new['PAYEE'].str.replace('.','') #make names consistent
    df_turnover_new['PAYEE']=df_turnover_new['PAYEE'].str.strip()
    df_turnover_new['PAYEE']=df_turnover_new['PAYEE'].str.replace(',',' ')
    df_turnover_new['PAYEE']=df_turnover_new['PAYEE'].str.replace('  ',' ')
    df_turnover_new.set_index('BIOGUIDE_ID', inplace=True)
    df_turnover_new=df_turnover_new.drop_duplicates(keep="first")
    list_rep_ID_new=df_turnover_new.reset_index()['BIOGUIDE_ID'].drop_duplicates(keep="first").reset_index().drop(['index'], axis=1)['BIOGUIDE_ID'].tolist()
    list_rep_ID_joined=list(set(list_rep_ID_new) - set(list_rep_ID_old))
    list_rep_ID_left=list(set(list_rep_ID_old) - set(list_rep_ID_new))
    for joined_rep_ID in list_rep_ID_joined: # add row for new reps
        df_rep_data.loc[joined_rep_ID]=np.NaN
        df_rep_data.loc[joined_rep_ID,'YEAR JOINED']=i
        df_rep_data.loc[joined_rep_ID,'YEAR LEFT']=2017
    for left_rep_ID in list_rep_ID_left:
        df_rep_data.loc[left_rep_ID,'YEAR LEFT']=i
    list_rep_ID_current=list(set(list_rep_ID_old) - set(list_rep_ID_left))    
    for rep_ID in list_rep_ID_current:
        list_rep_staff_old=df_turnover_old['PAYEE'][rep_ID].tolist()
        try:
            list_rep_staff_new=df_turnover_new['PAYEE'][rep_ID][rep_ID].tolist()
        except:
            list_rep_staff_new=[df_turnover_new['PAYEE'][rep_ID]]
        list_rep_staff_diff=list(set(list_rep_staff_old) - set(list_rep_staff_new))
        turnover=len(list_rep_staff_diff)
        df_rep_data.loc[rep_ID,str(i)+' TURNOVER']=turnover/len(list_rep_staff_old)
    list_rep_ID_old=list_rep_ID_new
    df_rep_data[str(i)+' STAFF SIZE']=df_turnover_new.reset_index().groupby('BIOGUIDE_ID')['PAYEE'].nunique()
    df_turnover_old=df_turnover_new
criteria_turnover=((df_rep_data['YEAR LEFT']-df_rep_data['YEAR JOINED'])>=4)
for i in  range(2011 , 2017):
    criteria_turnover=criteria_turnover & (df_rep_data[str(i)+' STAFF SIZE']>=5)
for i in range(2011 , 2017):    
    array_turnover[i-2011]=df_rep_data[str(i)+' TURNOVER'][criteria_turnover].mean()
print('Q6 - median of staff turnover (2011-2016):  ',(array_turnover[3]+array_turnover[3])/2,sep="")

#Q7
congress = Congress('h3jNxA0rvr4CYIfSCOXgVaq1Evr7Bis5WM8NCRva')
df_2016=df_all[['BIOGUIDE_ID','AMOUNT']][(df_all['START DATE'].dt.year==2016) & (df_all['BIOGUIDE_ID'].notna())]
pivot_2016=pd.pivot_table(df_2016,index=["BIOGUIDE_ID"],values = 'AMOUNT',aggfunc=np.sum).sort_values(by='AMOUNT', ascending=False, na_position='first').head(20) # top twenty spenders in 2016
pivot_2016['PARTY']=0
for i in range(0,20):
    dict_ID_info=congress.members.get(pivot_2016.index[i])
    if pd.DataFrame(dict_ID_info)['current_party'][0]=='D':        
        pivot_2016.loc[pivot_2016.index[i],'PARTY']=1
dem_sepnd_perc=(pivot_2016['PARTY']*pivot_2016["AMOUNT"]).sum()/(pivot_2016["AMOUNT"]).sum()
print('Q7 - fraction of top 20 Democratic members spending (2016):  ',dem_sepnd_perc,sep="")
    
