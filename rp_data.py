import numpy as np
import pandas as pd
from scipy import stats
from bootstrap import *

class rp_data():
  def __init__(self, dfs):
    '''
    Instantiates a relief pitcher data class using lists of dataframes

    Parameters
    ----------
    dfs - list of dataframes

    '''
    self.dfs = dfs
    years = pd.concat(self.dfs)
    self.years = years.file_year_x.unique()

  def __str__(self):
    '''
    Output when you print the class

    Returns
    ----------
    
    Str of the years in the data set.

    '''
    return f"The years in this data set range from {self.years[-1]} to {self.years[0]}."

  def year(self, year_of_interest):
    '''
    Returns year of the index given as a check

    Parameters
    ----------
    year - int of year of interest
     
    Returns
    ----------
    idx of dataframe that corresponds to year

    '''
    year_to_find = str(year_of_interest)
    self.idx = ''
    for num in range(len(self.dfs)):
      if self.dfs[num].file_year_x.unique()[0] == year_to_find:
        self.idx = num
        break
    return self.idx

  def separate_df(self, idx, percentile):
    '''
    Separates the df into higher paid and lower paid salary groups by percentile

    Parameters
    ----------
    idx - index of dataframe

    percentile - int of percentile to split dataframe by


    Returns
    ----------
    Tuple of two dataframes, one dataframe of the higher paid group and the other of the lower paid group.

    '''
    dfs = self.dfs
    salary = dfs[idx].Salary
    cut_off = np.percentile(salary, percentile)
    self.higher_paid, self.lower_paid = dfs[idx][salary >= cut_off], dfs[idx][salary < cut_off]
    return (self.higher_paid, self.lower_paid)

  def return_stats(self, year, percentile, col_name):
    '''
    Draw p-values and means of samples from dataframes and columns of interest separating dataframe entries by percentiles
    using student's t-test.

    Parameters
    ----------
    year - int of year of interest
    
    percentile - int of percentile to split dataframe by

    col_name - str of column name of interest 

    Returns
    -------
    Tuple of pvalue, mean of the column from the higher paid group, mean of the column from the lower paid group

    '''
    idx = self.year(year)
    df = self.dfs[idx]
    higher_paid, lower_paid = self.separate_df(idx, percentile)
    column1, column2 = higher_paid[f'{col_name}'], lower_paid[f'{col_name}']
    t_stat, pvalue = stats.ttest_ind(column1, column2)
    return pvalue, column1.mean(), column2.mean()

  def create_df(self, year, percentile, col_names):
    '''
    Create a dataframe of pvalues, means of columns tested.

    Parameters
    ----------
    year - int of year of interest
    
    percentile - int of percentile to split dataframe by

    col_names - list of str of column names of interest 

    Returns
    -------
    Dataframe showing pvalues, means of the columns from the higher paid group, means of the columns from the lower paid group
    
    '''
    idx = self.year(year)
    pvalues = []
    hp_means = []
    lp_means = []
    for col_name in col_names:
      pvalue, hp_mean, lp_mean = self.return_stats(year, percentile, col_name)
      pvalues.append(pvalue)
      hp_means.append(hp_mean)
      lp_means.append(lp_mean)
    d = {'p-values': pvalues, 'hp_means': hp_means, 'lp_means': lp_means}  
    df = pd.DataFrame(d, index=[col_names]) 
    return df

  def sum_data(self, percentile, col_name):
    '''
    Draw p-values and means of samples from the sum of all dataframes and 
    columns of interest separating dataframe entries by percentiles using student's t-test.

    Parameters
    ----------
    percentile - int of percentile to split dataframes by

    col_name - str of column name of interest 

    Returns
    -------
    Tuple of pvalue, mean of the column from the higher paid group, mean of the column from the lower paid group

    '''
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
    Create a dataframe of the sum of all dataframes imported of pvalues, means of columns tested.

    Parameters
    ----------
    percentile - int of percentile to split dataframes by

    col_names - list of str of column names of interest 

    Returns
    -------
    Dataframe showing pvalues, means of the columns from the higher paid group, means of the columns from the lower paid group of the sum of all years

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

  def IS(self, year, percentile):
    '''
    Print a str of the means of inherited runners scored % by higher paid and lower paid group with the p-value.

    Parameters
    ----------
    year - int of year of interest
    
    percentile - int of percentile to split dataframes by

    Returns
    -------
    str

    '''
    idx = self.year(year)
    df = self.dfs[idx]
    salary = df.Salary
    cut_off = np.percentile(salary, percentile)
    higher_paid, lower_paid = df[salary >= cut_off].drop('SV%', axis=1).dropna(), df[salary < cut_off].drop('SV%', axis=1).dropna()
    column1, column2 = higher_paid['IS%'].map(clean_char), lower_paid['IS%'].map(clean_char)
    t_stat, pvalue = stats.ttest_ind(column1, column2)
    year = df.file_year_x.unique()[0]
    return print(f'For the MLB season of {year}, the inherited runners scored % for the higher paid group is {column1.mean()}\nand the lower paid group % is {column2.mean()} with a p-value of {pvalue}.')

  def SV(self, year, percentile):
    '''
    Print a str of the means of save opportunities converted % by higher paid and lower paid group with the p-value.

    Parameters
    ----------
    year - int of year of interest
    
    percentile - int of percentile to split dataframes by

    Returns
    -------
    str

    '''
    idx = self.year(year)
    df = self.dfs[idx]
    salary = df.Salary
    cut_off = np.percentile(salary, percentile)
    higher_paid, lower_paid = df[salary >= cut_off].drop('IS%', axis=1).dropna(), df[salary < cut_off].drop('IS%', axis=1).dropna()
    column1, column2 = higher_paid['SV%'].map(clean_char), lower_paid['SV%'].map(clean_char)
    t_stat, pvalue = stats.ttest_ind(column1, column2)
    year = df.file_year_x.unique()[0]
    return print(f'For the MLB season of {year}, the save opportunities converted % for the higher paid group is {column1.mean()}\nand the lower paid group % is {column2.mean()} with a p-value of {pvalue}.')

  def bootstrap(self, year, percentile, col_name, n_simulations=10000):
    '''
    Resamples from a dataframe by percentile on the column of interest per # of simulations.
    Create a histogram of the bootstrapped data.

    Parameters
    ----------
    year - int of year of interest
    
    percentile - int of percentile to split dataframes by

    col_name - column name of interest

    n_simulations - number of times to bootstrap, default to 10000

    Returns
    -------
    Histogram of the results with 95% CI, sample distribution means

    '''
    idx = self.year(year)
    hp, lp = self.separate_df(idx, percentile)
    bs_hp, bs_lp = bootstrap(np.array(hp[f'{col_name}']), n_simulations), bootstrap(np.array(lp[f'{col_name}']), n_simulations)
    higher_paid_bs, lower_paid_bs = [sample.mean() for sample in bs_hp], [sample.mean() for sample in bs_lp]
    self.lower_ci_hp, self.upper_ci_hp = np.percentile(higher_paid_bs, [2.5, 97.5])
    self.lower_ci_lp, self.upper_ci_lp = np.percentile(lower_paid_bs, [2.5, 97.5])
    self.hp_bs_mean = np.mean(higher_paid_bs)
    self.lp_bs_mean = np.mean(lower_paid_bs)
    fig, ax = plt.subplots(figsize = (12,4))
    ax.hist(higher_paid_bs, alpha=0.5, bins=20, label='Higher Paid')
    ax.hist(lower_paid_bs, alpha=0.5, bins=20, label ='Lower Paid')
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
    '''
    Prints results from bootstrapped data for readability

    Returns
    -------
    Str of 95% confidence interval bounds, sample distribution means

    '''
    return print(f'''
    The 95% confidence intervals for the higher paid group ranges from {self.lower_ci_hp} to {self.upper_ci_hp}.
    The lower paid group ranges from {self.lower_ci_lp} and {self.upper_ci_lp}.
    Means of the distribution - 
    Higher Paid Group: {self.hp_bs_mean}
    Lower Paid Group:{self.lp_bs_mean}
     ''')

  def bootstrap_sum(self, percentile, col_name, n_simulations=10000):
    '''
    Resamples from a sum of the dataframes imported by percentile on the column of interest per # of simulations.
    Create a histogram of the bootstrapped data.

    Parameters
    ----------
    idx - index of dataframe to test
    
    percentile - int of percentile to split dataframes by

    col_name - column name of interest

    n_simulations - number of times to bootstrap, default to 10000

    Returns
    -------
    Histogram of the results with 95% CI, sample distribution means

    '''
    high_paid = []
    low_paid = []
    for idx in range(len(self.dfs)):
      hp, lp = self.separate_df(idx, percentile)
      high_paid.append(hp)
      low_paid.append(lp)
    hps = pd.concat(high_paid)
    lps = pd.concat(low_paid)
    bs_hp, bs_lp = bootstrap(np.array(hps[f'{col_name}']), n_simulations), bootstrap(np.array(lps[f'{col_name}']), n_simulations)
    hp_bs_sum, lp_bs_sum = [sample.mean() for sample in bs_hp], [sample.mean() for sample in bs_lp]
    self.lower_ci_hp_sum, self.upper_ci_hp_sum = np.percentile(hp_bs_sum, [2.5, 97.5])
    self.lower_ci_lp_sum, self.upper_ci_lp_sum = np.percentile(lp_bs_sum, [2.5, 97.5])
    self.hp_bs_sum_mean = np.mean(hp_bs_sum)
    self.lp_bs_sum_mean = np.mean(lp_bs_sum)
    fig, ax = plt.subplots(figsize = (12,4))
    ax.hist(hp_bs_sum, alpha=0.5, bins=20, label = 'Higher Paid')
    ax.hist(lp_bs_sum, alpha=0.5, bins=20, label = 'Lower Paid')
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
    '''
    Prints results from the bootstrapped sum data for readability

    Returns
    -------
    Str of 95% confidence interval bounds, sample distribution means

    '''
    return print(f'''
    The 95% confidence intervals for the higher paid group ranges from {self.lower_ci_hp_sum} to {self.upper_ci_hp_sum}.
    The lower paid group ranges from {self.lower_ci_lp_sum} and {self.upper_ci_lp_sum}.
    Means of the distribution - 
    Higher Paid Group: {self.hp_bs_sum_mean}
    Lower Paid Group:{self.lp_bs_sum_mean}
     ''')

  def corr(self, year, percentile, col_name):
    '''
    Finds the pearson correlation coefficient of a given dataframe and column of interest separated by percentile.

    Parameters
    ----------
    year - int of year of interest

    percentile - int of percentile to separate df by

    col_name - str of column name of interest

    Returns
    -------
    Str of pearson correlation coefficients and their pvalues

    '''
    idx = self.year(year)
    hp, lp = self.separate_df(idx, percentile)
    l_corr, l_pvalue = stats.pearsonr(lp.Salary, lp[f'{col_name}'])
    h_corr, h_pvalue = stats.pearsonr(hp.Salary, hp[f'{col_name}'])
    print(f'For the lower paid pitcher group: \nThe correlation coefficent is {l_corr} and the p-value is {l_pvalue}')
    print(f'For the higher paid pitcher group: \nThe correlation coefficent is {h_corr} and the p-value is {h_pvalue}')

  def corr_sum(self, percentile, col_name):
    '''
    Finds the pearson correlation coefficient of the sum of the dataframes and column of interest separated by percentile.

    Returns
    -------
    Str of pearson correlation coefficients and their pvalues

    '''
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
    print(f'For the lower paid pitcher group: \nThe correlation coefficent is {l_corr} and the p-value is {l_pvalue}')
    print(f'For the higher paid pitcher group: \nThe correlation coefficent is {h_corr} and the p-value is {h_pvalue}')

  def scatter(self, year, percentile, col_name):
    '''
    Creates a scatter plot of a given dataframe by the salary and column of interest separated by percentile

    Parameters
    ----------
    year - int of year of interest

    percentile - int of percentile to separate df by

    col_name - str of column name of interest

    Returns
    -------
    Scatter plot

    '''
    idx = self.year(year)
    hp, lp = self.separate_df(idx, percentile)
    fig, ax = plt.subplots()
    ax.scatter(hp.Salary, hp[col_name], alpha =0.5, label='hp')
    ax.scatter(lp.Salary, lp[col_name], alpha=0.5, label='lp')
    ax.set_title(f'{year} Salary vs {col_name}')
    ax.set_xlabel('Salary')
    ax.set_ylabel(f'{col_name}')
    ax.legend()

def clean_char(val):
  '''
  Converts % string into float, will ignore NaN values

  Parameters
  ----------
  val - str

  Returns
  ----------
  float

  '''
  try:
      return float(val.replace("%", "")) / 100
  except:
      return 0
