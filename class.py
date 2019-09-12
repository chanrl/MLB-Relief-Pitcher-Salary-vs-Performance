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
    hps = pd.concat(high_paid)
    lps = pd.concat(low_paid)
    self.higher_paid_sum = hps
    self.lower_paid_sum = lps
    column1, column2 = hps[f'{col_name}'], lps[f'{col_name}']
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

  def bootstrap(self, idx, percentile, col_name, n_simulations=10000):
    hp, lp = self.separate_df(idx, percentile)
    bs_hp, bs_lp = bootstrap(np.array(hp[f'{col_name}']), n_simulations), bootstrap(np.array(lp[f'{col_name}']), n_simulations)
    higher_paid_bs, lower_paid_bs = [sample.mean() for sample in bs_hp], [sample.mean() for sample in bs_lp]
    self.lower_ci_hp, self.upper_ci_hp = np.percentile(higher_paid_bs, [2.5, 97.5])
    self.lower_ci_lp, self.upper_ci_lp = np.percentile(lower_paid_bs, [2.5, 97.5])
    self.hp_bs_mean = np.mean(higher_paid_bs)
    self.lp_bs_mean = np.mean(lower_paid_bs)
    fig, ax = plt.subplots(figsize = (12,4))
    ax.hist(higher_paid_bs, alpha=0.5, bins=20)
    ax.hist(lower_paid_bs, alpha=0.5, bins=20)
    ax.axvline(self.lower_ci_hp, color='blue', linestyle="--", alpha=0.5, label='Higher Paid 95% CI')
    ax.axvline(self.upper_ci_hp, color='blue', linestyle="--", alpha=0.5)
    ax.axvline(self.lower_ci_lp, color='red', linestyle="--", alpha=0.5, label='Lower Paid 95% CI')
    ax.axvline(self.upper_ci_lp, color='red', linestyle="--", alpha=0.5)
    ax.axvline(self.hp_bs_mean, color='green', linestyle="--", alpha=0.5, label='Higher Paid Mean')
    ax.axvline(self.lp_bs_mean, color='black', linestyle="--", alpha=0.5, label='Lower Paid Mean')
    ax.legend()
    year = hp.file_year_x.unique()[0]
    ax.set_xlabel(f'{col_name} means')
    ax.set_ylabel('Count')
    ax.set_title(f'{year} Bootstrapped {col_name} Sample Means Distribution')
    plt.show()
    plt.ion()

  def bootstrap_stats(self):
    return print(f'''
    The 95% confidence intervals for the higher paid group ranges from {self.lower_ci_hp} to {self.upper_ci_hp}.
    The lower paid group ranges from {self.lower_ci_lp} and {self.upper_ci_lp}.
    Means of the distribution - 
    Higher Paid Group: {self.hp_bs_mean}
    Lower Paid Group:{self.lp_bs_mean}
     ''')

  def bootstrap_sum(self, percentile, col_name, n_simulations=10000):
    high_paid = []
    low_paid = []
    for idx in range(len(self.dfs)):
      hp, lp = self.separate_df(idx, percentile)
      high_paid.append(hp)
      low_paid.append(lp)
    hp_5 = pd.concat(high_paid)
    lp_5 = pd.concat(low_paid)
    bs_hp, bs_lp = bootstrap(np.array(hp_5[f'{col_name}']), n_simulations), bootstrap(np.array(lp_5[f'{col_name}']), n_simulations)
    hp_bs_sum, lp_bs_sum = [sample.mean() for sample in bs_hp], [sample.mean() for sample in bs_lp]
    self.lower_ci_hp_sum, self.upper_ci_hp_sum = np.percentile(hp_bs_sum, [2.5, 97.5])
    self.lower_ci_lp_sum, self.upper_ci_lp_sum = np.percentile(lp_bs_sum, [2.5, 97.5])
    self.hp_bs_sum_mean = np.mean(hp_bs_sum)
    self.lp_bs_sum_mean = np.mean(lp_bs_sum)
    fig, ax = plt.subplots(figsize = (12,4))
    ax.hist(hp_bs_sum, alpha=0.5, bins=20)
    ax.hist(lp_bs_sum, alpha=0.5, bins=20)
    ax.axvline(self.lower_ci_hp_sum, color='blue', linestyle="--", alpha=0.5, label='Higher Paid 95% CI')
    ax.axvline(self.upper_ci_hp_sum, color='blue', linestyle="--", alpha=0.5)
    ax.axvline(self.lower_ci_lp_sum, color='red', linestyle="--", alpha=0.5, label='Lower Paid 95% CI')
    ax.axvline(self.upper_ci_lp_sum, color='red', linestyle="--", alpha=0.5)
    ax.axvline(self.hp_bs_sum_mean, color='green', linestyle="--", alpha=0.5, label='Higher Paid Mean')
    ax.axvline(self.lp_bs_sum_mean, color='black', linestyle="--", alpha=0.5, label='Lower Paid Mean')
    ax.legend()
    ax.set_xlabel(f'{col_name} means')
    ax.set_ylabel('Count')
    ax.set_title(f'Bootstrapped {col_name} Sample Means Distribution from {self.years[-1]} to {self.years[0]}.')
    plt.show()
    plt.ion()

  def bootstrap_sum_stats(self):
    return print(f'''
    The 95% confidence intervals for the higher paid group ranges from {self.lower_ci_hp_sum} to {self.upper_ci_hp_sum}.
    The lower paid group ranges from {self.lower_ci_lp_sum} and {self.upper_ci_lp_sum}.
    Means of the distribution - 
    Higher Paid Group: {self.hp_bs_sum_mean}
    Lower Paid Group:{self.lp_bs_sum_mean}
     ''')

  def corr(self, idx, percentile, col_name):
    hp, lp = self.separate_df(idx, percentile)
    l_corr, l_pvalue = stats.pearsonr(lp.Salary, lp[f'{col_name}'])
    h_corr, h_pvalue = stats.pearsonr(hp.Salary, hp[f'{col_name}'])
    print(f'For the lower paid pitcher group: The correlation coefficent is {l_corr} and the p-value is {l_pvalue}')
    print(f'For the higher paid pitcher group: The correlation coefficent is {h_corr} and the p-value is {h_pvalue}')

  def corr_sum(self, percentile, col_name):
    high_paid = []
    low_paid = []
    for idx in range(len(self.dfs)):
      hp, lp = self.separate_df(idx, percentile)
      high_paid.append(hp)
      low_paid.append(lp)
    hps = pd.concat(high_paid)
    lps = pd.concat(low_paid)
    l_corr, l_pvalue = stats.pearsonr(lps.Salary, lps[f'{col_name}'])
    h_corr, h_pvalue = stats.pearsonr(hps.Salary, hps[f'{col_name}'])
    print(f'For the lower paid pitcher group: The correlation coefficent is {l_corr} and the p-value is {l_pvalue}')
    print(f'For the higher paid pitcher group: The correlation coefficent is {h_corr} and the p-value is {h_pvalue}')

