import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from scipy import stats
import glob
import os
import re
from bootstrap import *
from rp_data import *

relievers_csv = glob.glob('data/*-reliever*')
relievers_csv.sort(reverse=True)
salaries_csv = glob.glob('data/*-value*')
salaries_csv.sort(reverse=True)

#Extracting file names into a list

relievers = []
salaries = []

for file in relievers_csv:
    path, filename = os.path.split(file)
    year = re.findall('\d\d\d\d', filename)[0] #find only strings of 4 digits
    temp_df = pd.read_csv(file)
    temp_df['file_year'] = year #append year as a column to file as a reference
    relievers.append(temp_df)

for file in salaries_csv:
    path, filename = os.path.split(file)
    year = re.findall('\d\d\d\d', filename)[0]
    temp_df = pd.read_csv(file)
    temp_df['file_year'] = year
    salaries.append(temp_df)

def clean_df(df):
  '''
  Function for cleaning up df for rows with values that have column names as str type.
  The tables scraped from baseball-reference consist of multiple tables joined together
  and the column names have been repeatedly scraped as row entries.
  Remove pitchers with NaN values on salary as there is no way to quantify their value in this study
  Select columns have useful values
  '''
  if 'Salary' in df:
    df.dropna(subset = ['Salary'], inplace=True)
  df = df[df['Name'] != 'Name']
  col_names = ['Name','Age','Tm', 'G_x', 'GR', 'SV%', 'IS%','RA9', 'RAA', 'RAR', 'WAA', 'WAR', 'file_year_x', 'file_year_y', 'Salary']
  df = df[col_names].reset_index(drop=True)
  df.rename(columns ={"IP_x":"IP", "G_x": "G"}, inplace=True)
  df['GR%'] = df['GR'].astype(int)/df['G'].astype(int)
  return df

def merge_df(df1, df2):
  '''
  df1, df2 = reliever and value dfs
  Merge the dfs using inner join because pitchers from {year}-value df includes all pitchers, starters and relievers.
  This way, it will eliminate all the non-relievers by only merging rows under pitchers listed in the reliever df.
  '''
  return pd.merge(df1, df2, how='inner', on =['Name', 'Age', 'Tm'])

dfs = [clean_df(merge_df(r, s)) for r, s in zip(relievers, salaries)]

def exclusion(df):
  return df[(df['GR%'] > .50) & (df['GR'].astype(int) > 5)]

dfs = [exclusion(df) for df in dfs]

#Need to change the salary amounts to float

def salary_to_int(df):
  df['Salary'] = df['Salary'].replace('[$,]', '', regex=True).astype(int)

def column_to_num(df, col_name, type=float):
  df[col_name] = df[col_name].astype(type)

col_names = ['RAA','RAR', 'RA9', 'WAA', 'WAR']

for df in dfs:
    df.reset_index(drop= True)
    salary_to_int(df)
    for col_name in col_names:
        column_to_num(df, col_name)