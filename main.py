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
  Function for cleaning up df for rows with values that have column names as str type.
  The tables scraped from baseball-reference consist of multiple tables joined together
  and the column names have been repeatedly scraped as row entries.
  Remove pitchers with NaN values on salary as there is no way to quantify their value in this study
  Remove columns, duplicate that will not be used
  '''
  if 'Salary' in df:
    df.dropna(subset = ['Salary'], inplace = True)
  df = df[df['Name'] != 'Name']
  df = df.drop(['Unnamed: 0_x', 'Unnamed: 0_y', 'Rk_x', 'GS', 'RA9def', 'RA9role', 'PPFp', 'RA9avg', 'WAA', '0DR',
   'WAAadj', 'WAR', 'waaWL%', '162WL%', 'Acquired', 'GF', 'Wgr', '1stIP', 'Ahd', 'Tie', 'Bhd', 'Pit/GR', 'IP_y', 'G_y', 'IPmult'], axis=1).reset_index()
  df.drop(['index'], axis=1, inplace=True)
  return df.rename(columns ={"IP_x":"IP", "G_x": "G"})                                                                                                                                                                               

def merge_df(df1, df2):
  '''
  df1, df2 = reliever and value dfs
  Merge the dfs using inner join because pitchers from {year}-value df includes all pitchers, starters and relievers.
  This way, it will eliminate all the non-relievers by only merging rows under pitchers listed in the reliever df.
  '''
  return pd.merge(df1, df2, how='inner', on =['Name', 'Age', 'Tm'])

df_2019 = clean_df(merge_df(r_2019, salary_2019))
df_2018 = clean_df(merge_df(r_2018, salary_2018))
df_2017 = clean_df(merge_df(r_2017, salary_2017))
df_2016 = clean_df(merge_df(r_2016, salary_2016))
df_2015 = clean_df(merge_df(r_2015, salary_2015))

dfs = [df_2019, df_2018, df_2017, df_2016, df_2015]
years_5 = pd.concat(dfs)

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