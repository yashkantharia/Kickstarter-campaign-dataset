#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 19:26:26 2020

@author: yash
"""
import glob
import pandas as pd
import json
import re
import datetime
#create a list of all csv files
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

#combine all files in the list
combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ],ignore_index=True)


len(combined_csv)

#list of all column names
names = combined_csv.columns.values.tolist()

#Select required columns for the new dataframe
df = combined_csv[['id','name','currency','launched_at','backers_count','blurb','category','converted_pledged_amount','country','creator','deadline','fx_rate','goal','pledged','slug','state','usd_pledged','usd_type','location']]
names_df = df.columns.values.tolist()

#get sub category
sub_cat=[]
for i in range(0,len(df)):
    t = json.loads(df['category'][i]).get('slug').split('/')[0]
    sub_cat.append(t)
   
#get main category
main_cat= []
for i in range(0,len(df)):
    t = json.loads(df['category'][i]).get('name')
    main_cat.append(t)
   
#get creator id
creator_id=[]
for i in range(0,len(df)):
    t = df['creator'][i]
    t = re.findall(r'(?<=id")(?:\s*\:\s*)(.{0,23}?")',str(t),re.IGNORECASE+re.DOTALL)[0]
    creator_id.append(int(re.search(r'\d+', t).group(0)))
   
#get blurb length
blurb_len =[]
for i in range(0,len(df)):
    if type(df['blurb'][i])==str:
        blurb_len.append(len(df['blurb'][i]))
    else:
        blurb_len.append(0)
   
#convert goal into USD using the FX rate
goal_usd =[]
for i in range(0,len(df)):
    goal_usd.append(df['goal'][i]*df['fx_rate'][i])
 
#get the city from location 
city = []
for i in range(0,len(df)):
    if type(df['location'][i])==str:
        t = json.loads(df['location'][i])
        city.append(t.get('name'))
    else:
        city.append("Unknown")
  
#calculate number of days from deadline and launched       
duration = []
for i in range(0,len(df)):
    delta = round((combined_csv['deadline'][i]-combined_csv['launched_at'][i])/(60*60*24))
    duration.append(delta)
    

#conver the days from unix epoch to YYYY-MM-DD format (UTC)
for i in range(0,len(df)):
    df['deadline'][i]= datetime.datetime.utcfromtimestamp(df['deadline'][i]).strftime('%Y-%m-%d %H:%M:%S')
    df['launched_at'][i]= datetime.datetime.utcfromtimestamp(df['launched_at'][i]).strftime('%Y-%m-%d %H:%M:%S')
    print(i)

#create a new dataframe and add the above lists to it and name the columns
d_new = pd.DataFrame(columns=['sub_category','main_category','creator_id','blurb_length','goal_usd','city','duration'])

d_new['sub_category']=sub_cat
d_new['main_category']=main_cat
d_new['creator_id']=creator_id
d_new['blurb_length']=blurb_len
d_new['goal_usd']=goal_usd
d_new['city']=city
d_new['duration']=duration

#Concat the datasets 
dataset = pd.concat([df,d_new],axis=1)

#Remove unwanted rows
dataset.drop(['category','goal' , 'fx_rate','location','creator','converted_pledged_amount','pledged','usd_type'], axis = 1, inplace=True)

#DROP NAN values
dataset = dataset.dropna()

#Rename column name state to status
dataset.rename(columns={'state': 'status'}, inplace=True)

#save CSV File 
dataset.to_csv('Kickstarter Campaigns DataSet.csv')
