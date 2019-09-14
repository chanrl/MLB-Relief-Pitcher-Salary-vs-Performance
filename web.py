from selenium import webdriver
import pandas as pd
import os
import glob
import re

# Have to use selenium because using panda to read html directly from the hyperlink only finds the first table.

# Using webdriver module in selenium, I needed to create a webdriver object that will start my chrome browser
# and navigate it to the link I specify. I can then output the page source locally.

def get_html(link):
    '''

      Returning page source from link

      Parameters
      ----------
      link: hyperlink for a page as str

      Returns
      -------
      Website source code as str
      
    '''

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    html = driver.page_source
    driver.quit()
    return html

def source_to_df(start_year, end_year, directory='rp_data', download=False):
  '''
      Downloads page source as panda dataframes to csv files from range of year to specified directory (default as /rp_data)
      if it doesn't already exist, if it does exist, it will read the csv files from the folder.
      Outputs as a tuple of reliever and salary dfs.

      Parameters
      ----------
      start_year - int of earliest year to scrape data as int e.g. 2015

      end_year - int of last year to scrape data as int e.g. 2019

      directory - str of directory name e.g 'data'

      source_to_df(2015, 2019, 'data')

      Returns
      -------
      Tuple of scraped relievers and salaries dataframes
  '''
  if download == True:
    for num in range(start_year, (end_year+1)):
      html = get_html(f'https://www.baseball-reference.com/leagues/MLB/{num}-value-pitching.shtml')
      table = pd.read_html(html)
      if os.path.exists(f'{directory}') == True:
        table[-1].to_csv(f'{directory}/{num}-value.csv')
      else:
        os.mkdir(f'{directory}')
        table[-1].to_csv(f'{directory}/{num}-value.csv')

    #Reliever stats for the last 5 years:
    for num in range(start_year, (end_year+1)):
      html = get_html(f'https://www.baseball-reference.com/leagues/MLB/{num}-reliever-pitching.shtml')
      table = pd.read_html(html)
      if os.path.exists(f'{directory}') == True:
        table[-1].to_csv(f'{directory}/{num}-reliever.csv')
      else:
        os.mkdir(f'{directory}')
        table[-1].to_csv(f'{directory}/{num}-reliever.csv')
  
  relievers_csv = glob.glob(f'{directory}/*-reliever*')
  relievers_csv.sort(reverse=True)
  salaries_csv = glob.glob(f'{directory}/*-value*')
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
  return (relievers, salaries)