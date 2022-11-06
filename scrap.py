#Python program to scrape website
#and save quotes from website
from contextlib import nullcontext
import requests
import time
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from requests.models import PreparedRequest
import re

def waitBrowserReady():
    timeout = 3
    time.sleep(timeout)
    #element_present = EC.presence_of_element_located((By.CLASS_NAME, 'listing-key-specs'))
    #WebDriverWait(browser, timeout).until(element_present)
    
def getCarList():
    content = browser.page_source
    soup = BeautifulSoup(content, 'html5lib')

    cars=[] # a list to store quotes

    table = soup.find('div', attrs = {'class':'search-page__results'})
    regex = re.compile("20[0-2][0-9] \([0-9][0-9] reg\)")

    for row in table.findAll('div',	attrs = {'class':'product-card-content'}):
                            
        price = row.find('div', attrs={'class':'product-card-pricing__price'}).span.text
        car={}
        car['price'] = int(price.removeprefix("£").replace(',', ''))
        ul = row.find("ul", attrs={'class': 'listing-key-specs'})
        if ul is None:
            continue

        specs = ul.findAll("li")

        for spec in specs:
            specText = spec.text
            if "miles" in specText:
                miles = int(specText.removesuffix(" miles").replace(',', ''))
                car["miles"] = miles
                continue
            elif "PS" in specText:
                ps = int(specText.removesuffix("PS").replace(',', ''))
                car["PS"] = ps
                continue
            
            if regex.match(specText) is not None:
                car["Reg"] = specText


        cars.append(car)
    
    return cars


url = "https://www.autotrader.co.uk/car-search?sort=mileage&postcode=nw104hn"
params = {'radius':'1500','make':'Toyota', 'model' : 'Yaris', 'ma' : 'Y', 'only-delivery-option' :'on','fuel-type':'Petrol Hybrid'}
req = PreparedRequest()
req.prepare_url(url, params)
url =req.url

options = Options()
#options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
options.add_argument("--log-level=3")

browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

browser.get(url)
waitBrowserReady()



content = browser.page_source


soup = BeautifulSoup(content, 'html5lib')

nextPageLink = soup.find('a', attrs={'class': "pagination--right__active"})

#pageLinks = [o.attrs['href'] for o in pagination.findAll('a', attrs={'data-to-top': 'true'})[0:-1]]

cars=getCarList()


while(nextPageLink):
    browser.get(nextPageLink.attrs['href'])
    waitBrowserReady()
    content = browser.page_source
    soup = BeautifulSoup(content, 'html5lib')
    cars += getCarList()
    nextPageLink = soup.find('a', attrs={'class': "pagination--right__active"})

print(cars)
browser.close()

filename = 'auto trader yaris nw.csv'
with open(filename, 'w', newline='') as f:
    w = csv.DictWriter(f,['price', 'miles', 'Reg' , 'PS'])
    w.writeheader()
    for car in cars:
        w.writerow(car)
