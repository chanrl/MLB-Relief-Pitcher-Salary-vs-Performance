from selenium import webdriver
import pandas as pd

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
driver.get('https://www.baseball-reference.com/leagues/MLB/2019-value-pitching.shtml')

html = driver.page_source
driver.quit()

driver2 = webdriver.Chrome(options=options)
driver2.get('https://www.baseball-reference.com/leagues/MLB/2019-reliever-pitching.shtml')

html2 = driver2.page_source
driver2.quit()

table1 = pd.read_html(html)
table2 = pd.read_html(html2)

salary_table = table1[38].dropna()
team_salary = table1[36]

relief_pitching_table = table2[39].dropna()
team_relief_pitching = table2[37]

table = pd.merge(relief_pitching_table, salary_table, how='inner', on =['Name', 'Age', 'Tm'])

table = table[table['Name'] != 'Name']

salary = table['Salary']