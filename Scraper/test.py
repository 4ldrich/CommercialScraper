from bs4 import BeautifulSoup
from bs4.dammit import encoding_res
from selenium import webdriver
import numpy as np
import pandas as pd
from time import sleep
import time
from collections import defaultdict


start = time.time()

# THIS IS ALL LAID OUT PROCEDURALLY, NOT NEAT AND ENCAPSULATED.
# WILL DO THAT LATER

BATCH_ATTEMPTS = 10

# Initialising stuff, needs to be done
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)


# Put the website, click past the cookie button
url = 'https://www.airbnb.co.uk/rooms/50328285?_set_bev_on_new_domain=1635549222_ZTBiYTI4Zjk5Nzc3&source_impression_id=p3_1635549223_zpDx5u44aOBcaV1p&guests=1&adults=1'

driver.get(url)
sleep(2)
cookie_button = driver.find_element_by_class_name("_1xiwgrva")
cookie_button.click()
sleep(0.5)

homePage_html = driver.find_element_by_xpath('//*')
homePage_html = homePage_html.get_attribute('innerHTML')
homePage_soup = BeautifulSoup(homePage_html, 'lxml')


if homePage_soup.find('span', {'class': '_1ne5r4rt'}) is None:
    print('yessss')
else:
    overall_rating = homePage_soup.find('span', {'class': '_1ne5r4rt'}).text
    print(overall_rating)
