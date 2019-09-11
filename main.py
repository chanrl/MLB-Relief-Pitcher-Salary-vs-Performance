import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

r_2019 = pd.read_csv('data/2019-reliever.csv')
r_2018 = pd.read_csv('data/2018-reliever.csv')
r_2017 = pd.read_csv('data/2017-reliever.csv')
r_2016 = pd.read_csv('data/2016-reliever.csv')
r_2015 = pd.read_csv('data/2015-reliever.csv')

r_5years = [r_2019, r_2018, r_2017, r_2016, r_2015]

salary_2019 = pd.read_csv('data/2019-value.csv')
salary_2018 = pd.read_csv('data/2018-value.csv')
salary_2017 = pd.read_csv('data/2017-value.csv')
salary_2016 = pd.read_csv('data/2016-value.csv')
salary_2015 = pd.read_csv('data/2015-value.csv')

salary_5years = [salary_2019, salary_2018, salary_2017, salary_2016, salary_2015]

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
  df = df.drop(['Unnamed: 0_x', 'Unnamed: 0_y', 'Rk_x', 'Rk_y', 'GS', 'RA9def', 'RA9role', 'PPFp', 'RA9avg', 'WAA', '0DR',
   'WAAadj', 'WAR', 'waaWL%', '162WL%', 'Acquired', 'GF', 'Wgr', '1stIP', 'Ahd', 'Tie', 'Bhd', 'Pit/GR', 'IP_y', 'G_y', 'IPmult'], axis=1).reset_index()
  df.drop(['index'], axis=1, inplace=True)
  df.rename(columns ={"IP_x":"IP", "G_x": "G"}, inplace = True)                                                                                                                                                                               
  return df


def merge_df(df1, df2):
  '''
  df1, df2 = reliever and value dfs
  Merge the dfs using inner join because pitchers from {year}-value df includes all pitchers, starters and relievers.
  This way, it will eliminate all the non-relievers by only merging rows under pitchers listed in the reliever df.
  '''
  return pd.merge(df1, df2, how='inner', on =['Name', 'Age', 'Tm'])

#creating the dfs per year and cleaning them

df_5years = [clean_df(merge_df(r, s)) for r, s in zip(r_5years, salary_5years)]

#I see that even after using inner join, there are some starting pitchers that entered the game in relief on occasion, and may throw the data off.
#I will make a new column for GR/G, and then exclude those that have entered a game in relief less than 50% of the time

def games_relieved(df):
  df['GR%'] = df['GR'].astype(int)/df['G'].astype(int)
  return df

#Panda query to see if exclusion will work as intended

#df_5years[0][df_5years[0]['GR%'] < .50]

#Yep, all these names look like starters. Good to exclude.

def exclude_starters(df):
  return df[df['GR%'] > .50]

# dfs = [games_relieved(df) for df in dfs]
# dfs = [exclude_starters(df) for df in dfs]
dfs = [games_relieved(df) for df in df_5years]
dfs = [exclude_starters(df) for df in df_5years]

#Need to change the salary amounts to float

def salary_to_int(df):
  df['Salary'] = df['Salary'].replace('[$,]', '', regex=True).astype(int)

def column_to_num(df, col_name, type=float):
  df[col_name] = df[col_name].astype(type)

def clean_char(val):
    try:
        return float(val.replace("%", "")) / 100
    except:
        return 0

def clean_column(df, col_name):
  df[col_name] = df[col_name].map(clean_char)

# df['SV%_clean'] = df['SV%'].map(clean_column) #drop the original whenever you feel good
# df[['SV%_clean', 'SV%']]

def no_NaN(df, col_name):
  '''
  df, col_name as string
  returns columns without NaN values
  '''
  return df[df[col_name].isna() == False]

for df in dfs:
  clean_column(df, 'SV%')
  salary_to_int(df)
  column_to_num(df, 'RA9')
  # strip_chars(df, 'SV%', '%')
  # strip_chars(df, 'IS%', '%')

#creating a df that is the sum of all data collected
years_5 = pd.concat(dfs)

df_2019 = dfs[0]
df_2018 = dfs[1]
df_2017 = dfs[2]
df_2016 = dfs[3]
df_2015 = dfs[4]

# dfs = [df_2019, df_2018, df_2017, df_2016, df_2015]


#start some initial plots

def salary_plot(df, col_name):
  '''
  df = dataframe, col_name as str type to plot against
  will always be plotting against salary as x-axis values
  '''
  x = no_NaN(df, col_name)
  x.plot.scatter(x='Salary', y=col_name)

# fig, ax = plt.subplots()
# salary_plot(df_2019, 'RA9')
# salary_plot(df_2019, 'SV%')
# #salary_plot(df_2019, 'IS%')

# plt.show()
# plt.ion()
# WAR = wins after replacement
# BSv = blown saves
# IS% = percentage of inherited runners scored

# #Always better to have more data than not enough
# RA9 # of runs allowed per 9
# RAA # of runs better than average
# RAR # of runs better above replacement level pitcher
# gmLI #Game entering leverage index 1 = avg, 1+ is high pressure
#data['result'] = data['result'].map(lambda x: x.lstrip('+-').rstrip('aAbBcC'))