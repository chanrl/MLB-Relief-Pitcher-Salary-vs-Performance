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

cols = ['RA9', 'RAA', 'RAR', 'WAA', 'WAR']