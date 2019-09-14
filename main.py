import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from scipy import stats
from web import *
from bootstrap import *
from data import *
from rp_data import *

#source_to_df(start year, end year, directory to save to, download data if needed)
relievers, salaries = source_to_df(2015, 2019, directory='temp', download=False)

dfs = [clean_df(merge_df(r, s)) for r, s in zip(relievers, salaries)]

# removes players who entered the game in relief less than 50% of the time and less than 5 times
# majority of starter pitchers and position players removed from sample data
dfs = [exclusion(df) for df in dfs]

col_names = ['RAA','RAR', 'RA9', 'WAA', 'WAR']

for df in dfs:
    df.reset_index(drop= True)
    salary_to_int(df)
    for col_name in col_names:
        column_to_num(df, col_name)

data = rp_data(dfs)

# Example functions with short descriptions. Full docstring in rp_data.py file
cols = ['RA9', 'RAA', 'RAR', 'WAA', 'WAR'] #Current working performance metrics with the script. SV% and IS% are edge cases with own functions below.

# create_df('year of interest', percentile to separate higher paid pitcher group by, performance metrics specified above in cols)
data.create_df('2019', 80, cols) # returns dataframe of the p-values and means of the performance metric of the higher paid(hp) and lower paid(lp) relief pitcher groups
data.create_sum_df(80, cols) # same as above but for the entire data set scraped

data.bootstrap('2019', 70, 'RAA', 10000) # returns bootstrapped sample distribution sampled from specified year and performance metric of interest, default at 10000 simulations
data.bootstrap_stats() # returns values of upper and lower CI of sample mean distribution, sample distribution means of hp and lp groups

data.bootstrap_sum(80, 'RAA', 10000) # same as above but samples from the entire data set scraped
data.bootstrap_sum_stats() # returns values of upper and lower CI of sample mean distribution for the above, sample distribution means of hp and lp groups

data.corr('2019', 70, 'RAA') # returns pearsons correlation coefficient for salary vs performance metric specified using the year specified and percentile to separate by
data.corr_sum('2019', 70) # same as above but for the entire data set scraped
data.scatter('2019', 80, 'RAA') # plots salary vs performance metric on the year specified

##edge cases
data.IS('2017', 80) #returns mean of inherited runners scored % of sample year with p values of hp/lp pitcher groups separated by percentile 
data.SV('2018', 70) #returns mean of save opportunities converted % of sample year with p values of hp/lp pitcher groups separated by percentile
