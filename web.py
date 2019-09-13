from selenium import webdriver
import pandas as pd

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


if __name__ == "__main__":
  #Pitching stats for both starting and relief pitcher for last 5 years, has salary info:
  for num in range(2015, 2020):
    html = get_html(f'https://www.baseball-reference.com/leagues/MLB/{num}-value-pitching.shtml')
    table = pd.read_html(html)
    table[-1].to_csv(f'data/{num}-value.csv')

  #Reliever stats for the last 5 years:
  for num in range(2015, 2020):
    html = get_html(f'https://www.baseball-reference.com/leagues/MLB/{num}-reliever-pitching.shtml')
    table = pd.read_html(html)
    table[-1].to_csv(f'data/{num}-reliever.csv')