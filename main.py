from selenium import webdriver
import pandas as pd

r_2019 = pd.read_csv('data/2019-reliever.csv')
r_2018 = pd.read_csv('data/2018-reliever.csv')
r_2017 = pd.read_csv('data/2017-reliever.csv')
r_2016 = pd.read_csv('data/2016-reliever.csv')
r_2015 = pd.read_csv('data/2015-reliever.csv')

salary_2019 = pd.read_csv('data/2019-value.csv')
salary_2018 = pd.read_csv('data/2018-value.csv')
salary_2017 = pd.read_csv('data/2017-value.csv')
salary_2016 = pd.read_csv('data/2016-value.csv')
salary_2015 = pd.read_csv('data/2015-value.csv')

def clean_df(df):
  '''
  Function for cleaning up df for rows with values that have column names as str type
  the tables scraped from baseball-reference are multiple tables joined together
  and the column names have been repeatedly scraped as a row entry.
  Also want to remove pitchers with NaN values on salary as there is no way to quantify their value in this study
  '''
  if 'Salary' in df:
    df.dropna(subset = ['Salary'])
  return df[df['Name'] != 'Name'].reset_index()


# team_salary = table1[36]

# team_relief_pitching = table2[37]

# table = pd.merge(relief_pitching_table, salary_table, how='inner', on =['Name', 'Age', 'Tm'])
# #Inner join was used on name, age, and team columns for 2 reasons: 
# # 1. salary_table has the salary for all pitchers, and we are only interested in relief pitchers from the relief_pitching_table
# # 2. There are players with the same names so age and team identifiers are needed to merge them correctly.
# #Additionally, players traded to different teams unfortunately cannot simply have their stats combined and averaged by their entries due to different sample size for games played.

# table = table[table['Name'] != 'Name'].reset_index()
# # Salary_table and relief_pitching_table have many rows where the values are the column names, due to each of them consisting of multiple tables merged into one.

# salary = table['Salary'] #player salary
# WAR = table['WAR'] #wins after replacement
# BSv = table['BSv'] #blown saves
# IS = table['IS%'] #percentage of inherited runners scored

# #Always better to have more data than not enough
# RA9 = table['RA9'] # of runs allowed per 9
# RAA = table['RAA'] # of runs better than average
# RAR = table['RAR'] # of runs better above replacement level pitcher
# gmLI = table['gmLI'] #Game entering leverage index 1 = avg, 1+ is high pressure
# IP = table['IP'] #innings pitched
# LGr = table['Lgr'] #losses in relief