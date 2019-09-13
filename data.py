import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from scipy import stats
import glob
import os
import re
from bootstrap import *

def clean_df(df):
  '''
  Returns a df with columns of interest, removes row entries that were column names,
  drop Salary NaN values, renames certain columns for readability.
  Also creates a games relieved % column
  
  Parameters
  ----------
  df: dataframe

  Returns
  -------
  New dataframe
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
  Merges two dataframes by name, age and team name via inner join

  Parameters
  ----------
  df1: dataframe
  df2: dataframe

  Returns
  -------
  Merged dataframe
  '''
  return pd.merge(df1, df2, how='inner', on =['Name', 'Age', 'Tm'])

def exclusion(df):
  '''
  Returns dataframe filtered by GR% and GR

  Parameters
  ----------
  df - dataframe

  Returns
  ----------
  filtered df

  '''
  return df[(df['GR%'] > .50) & (df['GR'].astype(int) > 5)]

def salary_to_int(df):
  '''
  Converts currency column in dataframe from str into int for given dataframe

  Parameters
  ----------
  df - dataframe

  Returns
  ----------
  dataframe with new salary column

  '''
  df['Salary'] = df['Salary'].replace('[$,]', '', regex=True).astype(int)

def column_to_num(df, col_name, type=float):
  '''
  Converts column values in dataframe from str into float as default

  Parameters
  ----------
  df - dataframe

  col_name - column name to convert

  type - float or int

  Returns
  ----------
  dataframe with converted column

  '''
  df[col_name] = df[col_name].astype(type)