from selenium import webdriver
import pandas as pd

def get_html(link, driver):
    '''
    helper function for returning html object from link
    INPUT:
    - hyperlink for a page
    - str, unique driver name for each instance, or else chromedriver will error out
    '''
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    html = driver.page_source
    driver.quit()
    return html

html = get_html('https://www.baseball-reference.com/leagues/MLB/2019-value-pitching.shtml', 'driver')
html2 = get_html('https://www.baseball-reference.com/leagues/MLB/2019-reliever-pitching.shtml', 'driver2')

table1 = pd.read_html(html)
table2 = pd.read_html(html2)
#Using pandas module to read scraped data as pandas DataFrame

salary_table = table1[38].dropna()
#dropped NaN values
team_salary = table1[36]

relief_pitching_table = table2[39].dropna()
#dropped NaN values
team_relief_pitching = table2[37]

table = pd.merge(relief_pitching_table, salary_table, how='inner', on =['Name', 'Age', 'Tm'])
#Inner join was used on name, age, and team columns for 2 reasons: 
# 1. salary_table has the salary for all pitchers, and we are only interested in relief pitchers from the relief_pitching_table
# 2. There are players with the same names so age and team identifiers are needed to merge them correctly.
#Additionally, players traded to different teams unfortunately cannot simply have their stats combined and averaged by their entries due to different sample size for games played.

table = table[table['Name'] != 'Name'].reset_index()
# Salary_table and relief_pitching_table have many rows where the values are the column names, due to each of them consisting of multiple tables merged into one.

salary = table['Salary'] #player salary
WAR = table['WAR'] #wins after replacement
BSv = table['BSv'] #blown saves
IS = table['IS%'] #percentage of inherited runners scored

#Always better to have more data than not enough
RA9 = table['RA9'] # of runs allowed per 9
RAA = table['RAA'] # of runs better than average
RAR = table['RAR'] # of runs better above replacement level pitcher
gmLI = table['gmLI'] #Game entering leverage index 1 = avg, 1+ is high pressure
IP = table['IP'] #innings pitched
LGr = table['Lgr'] #losses in relief