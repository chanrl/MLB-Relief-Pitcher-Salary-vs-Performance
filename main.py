import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from scipy import stats
import glob
import os
import re
from bootstrap import *

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
    df.dropna(subset = ['Salary'], inplace = True)
  df = df[df['Name'] != 'Name']
  col_names = ['Name','Age','Tm','IP_x', 'G_x', 'GR', 'IS%','RA9', 'RAA', 'RAR', 'WAA', 'WAR', 'file_year_x', 'file_year_y', 'Salary'] #'SV%'
  df = df[col_names].reset_index()
  #df = df.drop(['Unnamed: 0_x', 'Unnamed: 0_y', 'Rk_x', 'Rk_y', 'GS', 'RA9def', 'RA9role', 'PPFp', 'RA9avg', 'WAA', '0DR',
  #'WAAadj', 'WAR', 'waaWL%', '162WL%', 'Acquired', 'GF', 'Wgr', '1stIP', 'Ahd', 'Tie', 'Bhd', 'Pit/GR', 'IP_y', 'G_y', 'IPmult'], axis=1).reset_index()
  # selecting by col_names was less work than dropping col_names
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

df_5years = [clean_df(merge_df(r, s)) for r, s in zip(relievers, salaries)]

#I see that even after using inner join, there are some starting pitchers that entered the game in relief on occasion, and may throw the data off.
#I will make a new column for GR/G, and then exclude those that have entered a game in relief less than 50% of the time

def games_relieved(df):
  df['GR%'] = df['GR'].astype(int)/df['G'].astype(int)
  return df

#Panda query to see if exclusion will work as intended

#df_5years[0][df_5years[0]['GR%'] < .50]

#Yep, all these names look like starters. Good to exclude.

#Also going to exclude pitchers with less than 5 games played. It looks like there are a lot of position players who have pitched a couple of times that may skew the performance stats.

def exclusion(df):
  return df[(df['GR%'] > .50) & (df['GR'].astype(int) > 5)]

dfs = [games_relieved(df) for df in df_5years]
dfs = [exclusion(df) for df in df_5years]

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

for df in dfs:
  # clean_column(df, 'SV%')
  # clean_column(df, 'IS%')
  column_to_num(df, 'RAA', int)
  column_to_num(df, 'RAR', int)
  column_to_num(df, 'RA9')
  column_to_num(df, 'WAA')
  column_to_num(df, 'WAR')
  salary_to_int(df)

#creating a df that is the sum of all data collected
years_5 = pd.concat(dfs)

df_2019 = dfs[0]
df_2018 = dfs[1]
df_2017 = dfs[2]
df_2016 = dfs[3]
df_2015 = dfs[4]

# dfs = [df_2019, df_2018, df_2017, df_2016, df_2015]

def salary_list(df, percentile):
  '''
  split df into higher paid and lower paid dfs by percentile
  df = dataframe, percentile as int type
  return as tuple of higher paid, lower paid dfs
  '''
  salary = df.Salary
  cut_off = np.percentile(salary, percentile)
  higher_paid, lower_paid = df[salary > cut_off], df[salary < cut_off]
  return (higher_paid, lower_paid)

#returns p-values, means of column samples of interest
def return_stats(sample1, sample2, col_name):
  '''Draw p-values and means of samples from dataframes and columns of interest.

    Parameters
    ----------
    sample1: dataframe
      The data to draw the bootstrap samples from.
    
    sample2: dataframe
      The number of bootstrap samples to draw from x.
    
    col_name: column name as str

    Returns
    -------
    Tuple consisting of pvalue, mean of the column from sample 1, mean of the column from sample 2
  '''
  column1, column2 = sample1[f'{col_name}'], sample2[f'{col_name}']
  t_stat, pvalue = stats.ttest_ind(column1, column2)
  return (pvalue, column1.mean(), column2.mean())

def pitcher_groups(df, percentile, col_name):
  hp, lp = salary_list(df, percentile)
  pvalue, mean1, mean2 = return_stats(hp, lp, col_name)
  return (pvalue, mean1, mean2)


#running t-statistic on the sample means for relief pitchers who are in the top 30 percentile of pay vs the rest of the league
pitcher_groups(df_2019, 70, 'RAA')
pitcher_groups(df_2019, 70, 'RAA')

# running t-statistic on the sample means for relief pitchers who are separated by specified percentiles of pay vs rest of the league over the last 5 seasons
high_paid = []
low_paid = []

for df in dfs:
  hp, lp = salary_list(df, 90)
  high_paid.append(hp)
  low_paid.append(lp)

hp_5yrs = pd.concat(high_paid)
lp_5yrs = pd.concat(low_paid)

t_stat, pvalue = stats.ttest_ind(hp_5yrs.RA9, lp_5yrs.RA9)
t_stat, pvalue = stats.ttest_ind(hp_5yrs.RAA, lp_5yrs.RAA)

# looking at values for 2019 season
hp, lp = salary_list(df_2019, 70)
return_stats(hp, lp, 'RAA')

#bootstrapping samples for higher paid pitchers for the 2019 season
bs = bootstrap(np.array(hp.RAA), 10000)
x = [sample.mean() for sample in bs]

bs2 = bootstrap(np.array(lp.RAA), 10000)
y = [sample.mean() for sample in bs2]

fig, ax = plt.subplots(2,1, figsize=(12,4))
ax[0].hist(x)
ax[1].hist(y)

lower_ci, upper_ci = np.percentile(x, [2.5, 97.5])  

# plt.show()
# plt.ion()

bs_test = bootstrap(np.array(hp_5yrs.RAA), 10000)
x = [sample.mean() for sample in bs]

l_corr, l_pvalue = stats.pearsonr(lp['RAA'], lp['Salary'])
h_corr, h_pvalue = stats.pearsonr(hp.RAA, hp.Salary)

l_corr, l_pvalue = stats.pearsonr(lp_5yrs['RAA'], lp_5yrs['Salary'])
h_corr, h_pvalue = stats.pearsonr(hp_5yrs.RAA, hp_5yrs.Salary)

#pvalues are < .05 for all of the above. indicates that there is a significant difference in means between higher and lower paid pitchers.


# salary_2019, salary_2018, salary_2017, salary_2016, salary_2015 = []

# for percentile in range(50,100,10):
#   for df in dfs:
#     hp, lp = salary_list(df, percentile)

#t_stat, pvalue = stats.ttest_ind(higher_paid_5yrs.RA9, lower_paid_5yrs.RA9)

# WAA = wins above average 
# WAR = wins after replacement
# SV% = percentage of save opportunities converted
# IS% = percentage of inherited runners scored

# RA9 # of runs allowed per 9
# RAA # of runs better than average
# RAR # of runs better above replacement level pitcher

test = dfs[0].copy()
test['IS%'].dropna(inplace=True)
clean_column(test, 'IS%')
test['IS%'].dropna(inplace=True)

thp, tlp = salary_list(test, 70)
return_stats(thp, tlp, 'IS%')