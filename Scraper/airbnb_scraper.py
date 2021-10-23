from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import pandas as pd
from time import sleep
import time
from collections import defaultdict


start = time.time()

## THIS IS ALL LAID OUT PROCEDURALLY, NOT NEAT AND ENCAPSULATED. 
# WILL DO THAT LATER

BATCH_ATTEMPTS = 30

# Initialising stuff, needs to be done
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)


# Put the website, click past the cookie button
url = "https://www.airbnb.co.uk/"
driver.get(url)
sleep(2)
cookie_button= driver.find_element_by_class_name("_1xiwgrva")
cookie_button.click()
sleep(0.5)

# Click the I'm flexible to get to the product browser 
flexible_button = driver.find_element_by_link_text("I’m flexible")
flexible_button.click()
sleep(3)


##########################################################################
## Get the Headers and store titles and links to 'clicked header page'
##########################################################################

header_container = driver.find_element_by_class_name('_alkx2')
headers = header_container.find_elements_by_class_name('_e296pg')

categories = []
category_links = []
for header in headers:
    categories.append(header.text)
categories.remove('More')

for i in range(len(headers)):
    headers[i].click()
    if i!= len(headers) - 1:
        category_links.append(driver.current_url)
    sleep(1)

    if i == len(headers) - 1:
        sleep(0.5)
        more_menu = header_container.find_element_by_class_name('_jvh3iol')
        more_headers = more_menu.find_elements_by_class_name('_1r9yw0q6')

        for j in range(-1,len(more_headers)-1):
            if j == -1:
                j+=1
            more_menu = header_container.find_element_by_class_name('_jvh3iol')
            more_headers = more_menu.find_elements_by_class_name('_1r9yw0q6')
            sleep(0.5)
            categories.append(more_headers[j].text)
            more_headers[j].click()
            sleep(1)
            category_links.append(driver.current_url)
            headers[i].click()
            sleep(1)



#################################################################
# BEGIN SCRAPING
#################################################################

# The dataframe where the dictionary for each page will write to
df = pd.DataFrame()
# PRIMARY KEY and missing data count
ID = 10000
MISSING_DATA = 0


#######################  THE PROCEDURE FOR YIELDING DATA ############################
try:
    for category_no in range(len(categories)):

        driver.get(category_links[category_no])
        driver.execute_script("document.body.style.zoom='75%'")
        sleep(3)

        # Scrolling will 'lazy load' all 300 objects per header tab
        # Set to FALSE when testing/sampling
        SCROLLING = False
        if SCROLLING:
            SCROLL_PAUSE_TIME = 4
            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                sleep(SCROLL_PAUSE_TIME)
                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height



        for i in range(BATCH_ATTEMPTS):
            try:
                # After scrolling, Get HTML soup for whole page of 1 header
                homePage_html = driver.find_element_by_xpath('//*')
                homePage_html = homePage_html.get_attribute('innerHTML')
                homePage_soup = BeautifulSoup(homePage_html, 'html.parser')


                # Store all links for locations listed on page in array
                places_container = homePage_soup.find('div', class_ = '_ty2eq0')
                places = places_container.find_all('div', class_= '_1kmzzkf')
                place_links = np.array([])
                for place in places:
                    url = f"https://www.airbnb.co.uk{place.a['href']}"
                    place_links = np.append(place_links,url)
            except:
                pass

        ##########################################################################
        ## NOW, ITERATE OVER THE ARRAY OF LINKS. 300 IF SCROLLED, 
        # 20 IF NOT SCROLLED
        #########################################################################

        for place_link in place_links:

            try:

                # page_source = requests.get(place_link).text

                ## Soups the html on the page
                driver.get(place_link)
                sleep(5)
                homePage_html = driver.find_element_by_xpath('//*')
                homePage_html = homePage_html.get_attribute('innerHTML')
                homePage_soup = BeautifulSoup(homePage_html, 'html5lib')
                # The dictionary to write to csv later. 
                # This will refresh every time a new page is loaded. GOOD. Keeps memory complexity low
                to_write = defaultdict()


                # Primary Key: Unique ID
                to_write['ID'] = int(ID)

                # Category from headers
                to_write['Airbnb_Cat'] = categories[category_no]

                #### GETTING DATA
                #Title
                for i in range(BATCH_ATTEMPTS):
                    try:
                        title = homePage_soup.find('h1').text
                        to_write['Title'] = title
                        break
                    except:
                        continue



                #Location
                for i in range(BATCH_ATTEMPTS):
                    try:
                        location = homePage_soup.find('span', {'class': '_pbq7fmm'}).text.replace(',', '')
                        to_write['Location'] = location
                        break
                    except:
                        continue



                # Information
                for i in range(BATCH_ATTEMPTS):
                    try:
                        info = homePage_soup.find('div', {'class': '_xcsyj0'}).next_sibling.text
                        info = info.replace('·', '')
                        info = info.split(',')
                        clean_info = []
                        for i in info:
                            clean_info.append(i.strip())

                        for val in clean_info:
                            label = val.split()[1]
                            if label not in ['guests', 'guest', 'bedrooms', 'bedroom',
                                                'beds', 'bed', 'bathrooms' ,'bathroom']:
                                pass
                            else:
                                if label[-1] != 's':
                                    label += 's'
                                to_write[label] = val.split()[0]
                                
                    except:
                        continue

                
                # Number of Reviews
                for i in range(BATCH_ATTEMPTS):
                    try:
                        review_count = homePage_soup.find('span', {'class': '_142pbzop'}).text
                        review_count = review_count.replace('(','')
                        review_count = review_count.split(' ')
                        to_write['Review_count'] = review_count[0]
                        break
                    except:
                        continue



                # Star rating
                for i in range(BATCH_ATTEMPTS):
                    try:
                        overall_rating = homePage_soup.find('span', {'class': '_1ne5r4rt'}).text
                        to_write['Overall Rate'] = overall_rating
                        break
                    except:
                        continue



                # Price Per Night
                for i in range(BATCH_ATTEMPTS):
                    try:
                        price_pNight = homePage_soup.find('span', {'class': '_tyxjp1'}).text[1:]
                        to_write['Price (Night)'] = price_pNight
                        break
                    except:
                        continue



                # Sub ratings
                subrate_values = np.array([])
                for i in range(BATCH_ATTEMPTS):
                    try:
                        subratings_container = homePage_soup.find('div', class_= 'ciubx2o dir dir-ltr')
                        subratings = subratings_container.findChildren('div', recursive = False)
                        for subrating in subratings:
                            if subrating.div.div.div.text:
                                to_write[subrating.div.div.div.text + '_rate'] = \
                                    subrating.div.div.div.nextSibling.text
                        break
                    except:
                        continue        
                
                
                # How many amneties each location has
                for i in range(BATCH_ATTEMPTS):
                    try:
                        amenities_container = homePage_soup.find('div', class_ = 'b6xigss dir dir-ltr')
                        amenities_count = amenities_container.a.text
                        amenities_count = int(''.join(filter(str.isdigit, amenities_count)))
                        to_write['amenities_count'] = amenities_count
                        break

                    except:
                        continue

                to_write['URL'] = place_link


                df = df.append(to_write, ignore_index=True)

                ID +=1


            # For whatever reason, be it encoding error, etc., the specific page is ignored and the error doesnt break the program
            except:
                MISSING_DATA +=1
                pass
finally:
    df.to_csv('products.csv', index=False)

    end = time.time()

    length = end-start
    print('length: ', round(length/60,2), 'minutes')
    # print('Speed: ', length/len(df.index), 'seconds per object')
    # print('predicted for all: ', ((length/len(df.index)) * 7500)/3600, ' hours')
    print(df)
    print('Missing Data: ', MISSING_DATA)

################################################
# TO DO LIST:

    # Is it possible to make this faster?? Threading?
    # Proxy to get round the 'too many requests'
    # Obviously encapsulate and make it Object-Oriented
    # Docstring everything
    # Merge onto Repo 
    # Make Test Files etc
    # Make the setup files
