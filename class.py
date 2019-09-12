import numpy as np
import pandas as pd
from scipy import stats
from bootstrap import *


def clean_char(val):
    try:
        return float(val.replace("%", "")) / 100
    except:
        return 0

class rp_data():
  def __init__(self, dfs):
    '''
    Constructs a relief pitcher data instance with lists of dataframes
    '''
    self.dfs = dfs
    years = pd.concat(self.dfs)
    self.years = years.file_year_x.unique()

  def __str__(self):
    return f"The years in this data set range from {self.years[-1]} to {self.years[0]}."

  def separate_df(self, idx, percentile):
    '''
    split df into higher paid and lower paid dfs by percentile
    df = dataframe, percentile as int type
    return as tuple of higher paid, lower paid dfs
    '''
    dfs = self.dfs
    salary = dfs[idx].Salary
    cut_off = np.percentile(salary, percentile)
    self.higher_paid, self.lower_paid = dfs[idx][salary >= cut_off], dfs[idx][salary < cut_off]
    return (self.higher_paid, self.lower_paid)

  def return_stats(self, idx, percentile, col_name):
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
    df = self.dfs[idx]
    salary = df.Salary
    cut_off = np.percentile(salary, percentile)
    higher_paid, lower_paid = df[salary >= cut_off], df[salary < cut_off]
    column1, column2 = higher_paid[f'{col_name}'], lower_paid[f'{col_name}']
    t_stat, pvalue = stats.ttest_ind(column1, column2)
    return pvalue, column1.mean(), column2.mean()

  def create_df(self, idx, percentile, col_names):
    '''
    Parameters
    ----------
    col_names: list of column names as str
    
    '''
    pvalues = []
    hp_means = []
    lp_means = []
    for col_name in col_names:
      pvalue, hp_mean, lp_mean = self.return_stats(idx, percentile, col_name)
      pvalues.append(pvalue)
      hp_means.append(hp_mean)
      lp_means.append(lp_mean)
    d = {'p-values': pvalues, 'hp_means': hp_means, 'lp_means': lp_means}  
    df = pd.DataFrame(d, index=[col_names]) 
    return df

  def sum_data(self, percentile, col_name):
    high_paid = []
    low_paid = []
    for idx in range(len(self.dfs)):
      hp, lp = self.separate_df(idx, percentile)
      high_paid.append(hp)
      low_paid.append(lp)
    hp_5 = pd.concat(high_paid)
    lp_5 = pd.concat(low_paid)
    column1, column2 = hp_5[f'{col_name}'], lp_5[f'{col_name}']
    t_stat, pvalue = stats.ttest_ind(column1, column2)
    return (pvalue, column1.mean(), column2.mean())

  def create_sum_df(self, percentile, col_names):
    '''
    Parameters
    ----------
    col_names: list of column names as str
    '''

    pvalues = []
    hp_means = []
    lp_means = []
    for col_name in col_names:
      pvalue, hp_mean, lp_mean = self.sum_data(percentile, col_name)
      pvalues.append(pvalue)
      hp_means.append(hp_mean)
      lp_means.append(lp_mean)
    d = {'p-values': pvalues, 'hp_means': hp_means, 'lp_means': lp_means}
    df = pd.DataFrame(d, index=[col_names])
    return df

#The next two functions are edge cases where I was not too sure what to do with the NaN values. 
#I decided to drop the entries with NaN from the dataset since some relief pitchers may never be called upon a save situation or situation with runners on base.

  def IS(self, idx, percentile):
    df = self.dfs[idx]
    salary = df.Salary
    cut_off = np.percentile(salary, percentile)
    higher_paid, lower_paid = df[salary >= cut_off].drop('SV%', axis=1).dropna(), df[salary < cut_off].drop('SV%', axis=1).dropna()
    column1, column2 = higher_paid['IS%'].map(clean_char), lower_paid['IS%'].map(clean_char)
    t_stat, pvalue = stats.ttest_ind(column1, column2)
    year = df.file_year_x.unique()[0]
    return print(f'For the MLB season of {year}, the inherited runners scored % for the higher paid group is {column1.mean()}\nand the lower paid group % is {column2.mean()} with a p-value of {pvalue}.')

  def SV(self, idx, percentile):
    df = self.dfs[idx]
    salary = df.Salary
    cut_off = np.percentile(salary, percentile)
    higher_paid, lower_paid = df[salary >= cut_off].drop('IS%', axis=1).dropna(), df[salary < cut_off].drop('IS%', axis=1).dropna()
    column1, column2 = higher_paid['SV%'].map(clean_char), lower_paid['SV%'].map(clean_char)
    t_stat, pvalue = stats.ttest_ind(column1, column2)
    year = df.file_year_x.unique()[0]
    return print(f'For the MLB season of {year}, the save opportunities converted % for the higher paid group is {column1.mean()}\nand the lower paid group % is {column2.mean()} with a p-value of {pvalue}.')

  def bootstrap_col(self, idx, percentile, col_name, n_simulations=10000):
    hp, lp = self.separate_df(idx, percentile)
    bs_hp, bs_lp = bootstrap(np.array(hp[f'{col_name}']), n_simulations), bootstrap(np.array(lp[f'{col_name}']), n_simulations)
    higher_paid_bs, lower_paid_bs = [sample.mean() for sample in bs_hp], [sample.mean() for sample in bs_lp]
    fig, ax = plt.subplots(figsize = (12,4))
    ax.hist(higher_paid_bs, alpha=0.5, bins=20)
    ax.hist(lower_paid_bs, alpha=0.5, bins=20)
    plt.show()
    plt.ion()

  def sum_bootstrap(self, percentile, col_name, n_simulations=10000):
    high_paid = []
    low_paid = []
    for idx in range(len(self.dfs)):
      hp, lp = self.separate_df(idx, percentile)
      high_paid.append(hp)
      low_paid.append(lp)
    hp_5 = pd.concat(high_paid)
    lp_5 = pd.concat(low_paid)
    bs_hp, bs_lp = bootstrap(np.array(hp_5[f'{col_name}']), n_simulations), bootstrap(np.array(lp_5[f'{col_name}']), n_simulations)
    self.hp_bs_sum, self.lp_bs_sum = [sample.mean() for sample in bs_hp], [sample.mean() for sample in bs_lp]
    return (self.hp_bs_sum, self.lp_bs_sum)

#   def bootstrap_dist(bs_data, bins_num, idx):
#     hp, lp = bs_data
#   ax[idx].hist(hp, alpha=0.5, bins=bins_num)
#   ax[idx].hist(lp, alpha=0.5, bins=bins_num)

# bs_2019_50 = bootstrap_col(df_2019, 50, 'RAA')
# bs_2019_60 = bootstrap_col(df_2019, 60, 'RAA')
# bs_2019_70 = bootstrap_col(df_2019, 70, 'RAA')
# bs_2019_80 = bootstrap_col(df_2019, 80, 'RAA')

# fig, ax = plt.subplots(1,4, figsize=(12,4))

