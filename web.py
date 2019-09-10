from selenium import webdriver
import pandas as pd

def get_html(link):
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



#Value pitching for last 5 years:
for num in range(2015, 2020):
 html = get_html(f'https://www.baseball-reference.com/leagues/MLB/{num}-value-pitching.shtml')
 table = pd.read_html(html)
 table[-1].to_csv(f'data/{num}-value.csv')

#Reliever stats for the last 5 years:
for num in range(2015, 2020):
  html = get_html(f'https://www.baseball-reference.com/leagues/MLB/{num}-reliever-pitching.shtml')
  table = pd.read_html(html)
  table[-1].to_csv(f'data/{num}-reliever.csv')

# #Using pandas module to read scraped data as pandas DataFrame

# table1.to_csv('test.csv')