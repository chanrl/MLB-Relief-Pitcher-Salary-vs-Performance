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
  col_names = ['Name','Age','Tm','IP_x', 'G_x', 'GR', 'SV%', 'IS%','RA9', 'RAA', 'RAR', 'WAA', 'WAR', 'file_year_x', 'file_year_y', 'Salary']
  df = df[col_names].reset_index()
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

#Creating objects for each of the dfs
df_2019 = dfs[0]
df_2018 = dfs[1]
df_2017 = dfs[2]
df_2016 = dfs[3]
df_2015 = dfs[4]

def separate_df(df, percentile):
  '''
  split df into higher paid and lower paid dfs by percentile
  df = dataframe, percentile as int type
  return as tuple of higher paid, lower paid dfs
  '''
  salary = df.Salary
  cut_off = np.percentile(salary, percentile)
  higher_paid, lower_paid = df[salary >= cut_off], df[salary < cut_off]
  return (higher_paid, lower_paid)

#returns p-values, means of column samples of interest

def return_stats(df, percentile, col_name):
  '''
    Draw p-values and means of samples from dataframes and columns of interest separating dataframe entries by percentiles.

    Parameters
    ----------
    sample1: dataframe
      The data to separate into two groups of higher paid and lower paid by given percentile
    
    col_name: column name as str

    Returns
    -------
    Tuple consisting of pvalue, mean of the column from the higher paid group, mean of the column from the lower paid group
  '''
  salary = df.Salary
  cut_off = np.percentile(salary, percentile)
  higher_paid, lower_paid = df[salary >= cut_off], df[salary < cut_off]
  column1, column2 = higher_paid[f'{col_name}'], lower_paid[f'{col_name}']
  t_stat, pvalue = stats.ttest_ind(column1, column2)
  return (pvalue, column1.mean(), column2.mean())

#Create a table with different percentiles and stats for the 2019 year

def create_df(df, percentile, col_names):
  '''
  Parameters
  ----------
  col_names: list of column names as str
  
  '''

  pvalues = []
  hp_means = []
  lp_means = []
  for col_name in col_names:
    pvalue, hp_mean, lp_mean = return_stats(df_2019, percentile, col_name)
    pvalues.append(pvalue)
    hp_means.append(hp_mean)
    lp_means.append(lp_mean)
  d = {'p-values': pvalues, 'hp_means': hp_means, 'lp_means': lp_means}  
  df = pd.DataFrame(d, index=[col_names]) 
  return df

#columns I am interested in:
col_names = ['RA9', 'RAA', 'RAR', 'WAA', 'WAR']

dfs_means = [create_df(df_2019, num, col_names) for num in range(50,100,10)]

means_50 = dfs_means[0]
means_60 = dfs_means[1]
means_70 = dfs_means[2]
means_80 = dfs_means[3]
means_90 = dfs_means[4]

# running t-statistic on the sample means for relief pitchers who are separated by specified percentiles of pay vs rest of the league over the last 5 seasons
# can't use existing functions as easily because if I simply combine the data from the start into a 5 year window and then perform the analysis, I may be mixing up the higher paid
# and lower paid pitchers if I don't separate by pay before concatenating.

def five_year(dfs, percentile, col_name):
  high_paid = []
  low_paid = []
  for df in dfs:
    hp, lp = separate_df(df, percentile)
    high_paid.append(hp)
    low_paid.append(lp)
  hp_5 = pd.concat(high_paid)
  lp_5 = pd.concat(low_paid)
  column1, column2 = hp_5[f'{col_name}'], lp_5[f'{col_name}']
  t_stat, pvalue = stats.ttest_ind(column1, column2)
  return (pvalue, column1.mean(), column2.mean())

def create_five_year_df(dfs, percentile, col_names):
  '''
  Parameters
  ----------
  col_names: list of column names as str
  '''

  pvalues = []
  hp_means = []
  lp_means = []
  for col_name in col_names:
    pvalue, hp_mean, lp_mean = five_year(dfs, percentile, col_name)
    pvalues.append(pvalue)
    hp_means.append(hp_mean)
    lp_means.append(lp_mean)
  d = {'p-values': pvalues, 'hp_means': hp_means, 'lp_means': lp_means}
  df = pd.DataFrame(d, index=[col_names])
  return df

#bootstrapping samples for higher paid pitchers for the 2019 season
def bootstrap_col(df, percentile, col_name, n_simulations=10000):
  hp, lp = separate_df(df, percentile)
  bs_hp, bs_lp = bootstrap(np.array(hp[f'{col_name}']), n_simulations), bootstrap(np.array(lp[f'{col_name}']), n_simulations)
  higher_paid, lower_paid = [sample.mean() for sample in bs_hp], [sample.mean() for sample in bs_lp]
  return (higher_paid, lower_paid)

def five_year_bs(dfs, percentile, col_name, n_simulations=10000):
  high_paid = []
  low_paid = []
  for df in dfs:
    hp, lp = separate_df(df, percentile)
    high_paid.append(hp)
    low_paid.append(lp)
  hp_5 = pd.concat(high_paid)
  lp_5 = pd.concat(low_paid)
  bs_hp, bs_lp = bootstrap(np.array(hp_5[f'{col_name}']), n_simulations), bootstrap(np.array(lp_5[f'{col_name}']), n_simulations)
  higher_paid, lower_paid = [sample.mean() for sample in bs_hp], [sample.mean() for sample in bs_lp]
  return (higher_paid, lower_paid)

def graph_bootstrap(bs_data, bins_num, idx):
  hp, lp = bs_data
  ax[idx].hist(hp, alpha=0.5, bins=bins_num)
  ax[idx].hist(lp, alpha=0.5, bins=bins_num)

bs_2019_50 = bootstrap_col(df_2019, 50, 'RAA')
bs_2019_60 = bootstrap_col(df_2019, 60, 'RAA')
bs_2019_70 = bootstrap_col(df_2019, 70, 'RAA')
bs_2019_80 = bootstrap_col(df_2019, 80, 'RAA')

fig, ax = plt.subplots(1,4, figsize=(12,4))

# graph_bootstrap(bs_2019_50, 20, 0)
# lower_ci, upper_ci = np.percentile(bs_2019_50[0], [2.5, 97.5])  
# graph_bootstrap(bs_2019_60, 20, 1)
# lower_ci, upper_ci = np.percentile(bs_2019_60[0], [2.5, 97.5])  
# graph_bootstrap(bs_2019_70, 20, 2)
# lower_ci, upper_ci = np.percentile(bs_2019_70[0], [2.5, 97.5])  
# graph_bootstrap(bs_2019_80, 20, 3)
# lower_ci, upper_ci = np.percentile(bs_2019_80[0], [2.5, 97.5])

# plt.show()
# plt.ion()
bs_5_50 = five_year_bs(dfs, 50, 'RAA')
bs_5_60 = five_year_bs(dfs, 60, 'RAA')
bs_5_70 = five_year_bs(dfs, 70, 'RAA')
bs_5_80 = five_year_bs(dfs, 80, 'RAA')

graph_bootstrap(bs_5_50, 20, 0)
#lower_ci, upper_ci = np.percentile(bs_2019_50[0], [2.5, 97.5])  
graph_bootstrap(bs_5_60, 20, 1)
#lower_ci, upper_ci = np.percentile(bs_2019_60[0], [2.5, 97.5])  
graph_bootstrap(bs_5_70, 20, 2)
#lower_ci, upper_ci = np.percentile(bs_2019_70[0], [2.5, 97.5])  
graph_bootstrap(bs_5_80, 20, 3)
#lower_ci, upper_ci = np.percentile(bs_2019_80[0], [2.5, 97.5])

plt.show()

def corr_RAA(df, percentile):
  hp, lp = separate_df(df, percentile)
  l_corr, l_pvalue = stats.pearsonr(lp.Salary, lp.RAA)
  h_corr, h_pvalue = stats.pearsonr(hp.Salary, hp.RAA)
  print(f'For the lower paid pitcher group: The correlation coefficent is {l_corr} and the p-value is {l_pvalue}')
  print(f'For the higher paid pitcher group: The correlation coefficent is {h_corr} and the p-value is {h_pvalue}')

def corr_RAA_5yr(dfs, percentile):
  high_paid = []
  low_paid = []
  for df in dfs:
    hp, lp = separate_df(df, percentile)
    high_paid.append(hp)
    low_paid.append(lp)
  hp_5 = pd.concat(high_paid)
  lp_5 = pd.concat(low_paid)
  l_corr, l_pvalue = stats.pearsonr(lp_5.Salary, lp_5.RAA)
  h_corr, h_pvalue = stats.pearsonr(hp_5.Salary, hp_5.RAA)
  print(f'For the lower paid pitcher group: The correlation coefficent is {l_corr} and the p-value is {l_pvalue}')
  print(f'For the higher paid pitcher group: The correlation coefficent is {h_corr} and the p-value is {h_pvalue}')

corr_RAA(df_2019, 80)

corr_RAA_5yr(dfs, 80)
# this one is difficult to graph the correlation. pearsons correlation coefficient is a measure of the linear correlation between 2 variables.
# it's possible that without adjusting salaries for inflation by year, it will not be possible to see a linear relationship. 
# In 2015, the highest paid reliever was getting 10million, vs 20 mil in 2019.
max_2015, max_2019 = (dfs[4].Salary.max(), dfs[0].Salary.max())

# def test(dfs, percentile, col_names):
#   '''
#   Parameters
#   ----------
#   col_names: list of column names as str
#   '''
#   if dfs == list:
#     pvalues = []
#     hp_means = []
#     lp_means = []
#     for col_name in col_names:
#       pvalue, hp_mean, lp_mean = five_year(dfs, percentile, col_name)
#       pvalues.append(pvalue)
#       hp_means.append(hp_mean)
#       lp_means.append(lp_mean)
#     d = {'p-values': pvalues, 'hp_means': hp_means, 'lp_means': lp_means}
#     df = pd.DataFrame(d, index=[col_names])
#     return df
#   else:
#     pvalues = []
#     hp_means = []
#     lp_means = []
#     for col_name in col_names:
#       pvalue, hp_mean, lp_mean = return_stats(df_2019, percentile, col_name)
#       pvalues.append(pvalue)
#       hp_means.append(hp_mean)
#       lp_means.append(lp_mean)
#     d = {'p-values': pvalues, 'hp_means': hp_means, 'lp_means': lp_means}  
#     df = pd.DataFrame(d, index=[col_names]) 
#     return df

# WAA = wins above average 
# WAR = wins after replacement
# SV% = percentage of save opportunities converted
# IS% = percentage of inherited runners scored

# RA9 # of runs allowed per 9
# RAA # of runs better than average
# RAR # of runs better above replacement level pitcher