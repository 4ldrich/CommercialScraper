'''
Module description HERE

'''

from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import pandas as pd
from time import sleep
import time

class Scraper:
    '''
    SUMMARY OF THE SCRAPER.
    Scrapes AirBNB for data ... 
    '''

    def __init__(self):
        '''
        Initialising selenium webdriver
        Navigate past the cookie wall and home page onto the 
        "I'm feeling lucky" page Where there are 25 Airbnb categories, 
        with roughly 300 Airbnb products per category

        Attributes:
            sample (bool): when set to true locks scrolling, so only top 
            20 products per category are scraped
            BATCH_ATTEMPTS (int): allows for elements to not be loaded straight away
        '''
        self.BATCH_ATTEMPTS = 30
        self.main_url = "https://www.airbnb.co.uk/"

        # Initialising the selenium webdriver
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)

        # Getting the Airbnb url and clicking past the cookie wall
        self.driver.get(self.main_url)
        sleep(2)
        self._cookie_check_and_click()

        # Click the I'm flexible to get to the product browser 
        flexible_button = self.driver.find_element_by_link_text("I’m flexible")
        flexible_button.click()
        sleep(3)


    def _get_categories(self, count = 25):

        # The count variable is an input to stop the header yield at any given index of iteration
        # for example: if count was set to 3, then the loop below to collect header links/titles
        # would break on the third iteration.
        if count > 25:
            raise ValueError('Max amount of headers on Airbnb\'s website is 25')
        if count < 1:
            raise ValueError('Count must be a positive integer greater than 1')

        self._cookie_check_and_click()

        # START of the headr yield code. This uses seleniums webdriver
        # to both click through and catch the header names and urls of each of the
        # 25 headers. BS4 cannot get their hrefs easily because they're 'buttons' on the site!
        header_container = self.driver.find_element_by_class_name('_alkx2')
        headers = header_container.find_elements_by_class_name('_e296pg')

        # First, get the text for the headers up to the 'more'. (Not all headers are visible immediately)
        # if the count is lower than current visible headers, this is sliced at the bottom
        self.categories = []
        self.category_links = []
        for header in headers:
            self.categories.append(header.text)
        self.categories.remove('More')
        self.categories = self.categories[:count]

        # Click through the visible headers to get urls for each one (except for 'More')
        counted = 0
        for i in range(len(headers)):
            headers[i].click()
            if i!= len(headers) - 1:
                self.category_links.append(self.driver.current_url)
                counted +=1
                # Break the entire function if count is met
                if counted == count:
                    return
            sleep(1)

            # Click the 'More' header and get the elements for rest of headers whilet they're visible
            if i == len(headers) - 1:
                sleep(0.5)
                more_menu = header_container.find_element_by_class_name('_jvh3iol')
                more_headers = more_menu.find_elements_by_class_name('_1r9yw0q6')

                # The offset means indexing goes 0, 0, 1, 2, 3, 4,... because of the nature of the 'More' column
                for j in range(-1,len(more_headers)-1):
                    if j == -1:
                        j+=1
                    # Click the 'More' header and get the elements for rest of headers whilet they're visible
                    # the difficulty with sich a dynamic page is that this has to be repeatedly done
                    more_menu = header_container.find_element_by_class_name('_jvh3iol')
                    more_headers = more_menu.find_elements_by_class_name('_1r9yw0q6')
                    sleep(0.5)
                    # Get the category name from header
                    self.categories.append(more_headers[j].text)
                    more_headers[j].click()
                    sleep(0.5)
                    # After clicking that header, get the corresponding header url for it
                    self.category_links.append(self.driver.current_url)
                    headers[i].click()
                    counted+=1
                    # Break the entire function if count is met
                    if counted == count:
                        return
 

    def _get_products(self, header_url, SCROLLING = True):
        self.driver.get(header_url)
        sleep(0.5)
        self._cookie_check_and_click()
        self.driver.execute_script("document.body.style.zoom='75%'")
        sleep(3)

        # SCROLLING will 'lazy load' all ~300 objects per header tab
        # Set to FALSE when testing/sampling
        if SCROLLING:
            SCROLL_PAUSE_TIME = 4
            # Get scroll height
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                sleep(SCROLL_PAUSE_TIME)
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        for i in range(self.BATCH_ATTEMPTS):
            try:
                # After scrolling, Get HTML soup for whole page of 1 header
                homePage_html = self.driver.find_element_by_xpath('//*')
                homePage_html = homePage_html.get_attribute('innerHTML')
                homePage_soup = BeautifulSoup(homePage_html, 'html.parser')


                # Store all links for locations listed on page in array
                places_container = homePage_soup.find('div', class_ = '_ty2eq0')
                places = places_container.find_all('div', class_= '_1kmzzkf')
                self.product_links = np.array([])
                for place in places:
                    url = f"https://www.airbnb.co.uk{place.a['href']}"
                    self.product_links = np.append(self.product_links,url)
            except:
                pass


    

    def __is_cookie_button_present(self):
        for i in range(10):
            try:
                return self.driver.find_element_by_class_name("_1xiwgrva") is not None
            except:
                pass
        return False



    def _cookie_check_and_click(self):
        if self.__is_cookie_button_present():
            cookie_button= self.driver.find_element_by_class_name("_1xiwgrva")
            cookie_button.click()
            sleep(0.5)
        else:
            return


    @staticmethod 
    def string_clean(text: str, str_type) -> str:
        '''
        docstring here +++++++++++++
        '''

        if str_type == 'info':
            output = []
            # Organises the text into a clean list of 
            # ['x guests', 'x bedrooms', 'x beds', 'x bathrooms']
            # this is much easier to be iterated over and parsed
            text = text.replace('·', '')
            text = text.split(',')
            clean_info = []
            for i in text:
                clean_info.append(i.strip())
            
            for val in clean_info:
                label = val.split()[1]
                # unlikely to happen, but if theres an anomaly in the site text, 
                # the certain element is ignored and this doesn't mess up the data
                if label not in ['guests', 'guest', 'bedrooms', 'bedroom',
                    'beds', 'bed', 'bathrooms' ,'bathroom']:
                    pass

                
                else:
                    # An element with a count of '1' (e.g. 1 bedroom) has no 's' on the end, which 
                    # will confuse the dictionary and dataframe. So all singular instances have an 's' added
                    if label[-1] != 's':
                        label += 's'
                    # The output is a nested list: [['guests', x], ['bedrooms', x] ...] 
                    output.append([label, val.split()[0]])
            return output
        


        elif str_type == 'review count':
            # Gets rid of brackets if they are there
            text = text.replace('(','')
            text = text.replace(')','')
            # Split up the number and reviews string into [x, 'Reviews']
            text = text.split(' ')
            return text[0]
        

        elif str_type == 'amenities':
            # Simply filters out the numerical value in the text:
            # "Show all xx amenities"
            return int(''.join(filter(str.isdigit, text)))

        else:
            raise TypeError('Please specify a distinct part of the page to clean. Have you checked your spelling?')
    

    def scrape_product(self, product_url, ID, category):
        '''
        This function scrapes all relevant information from a single Airbnb
        product page. 
        MORE HERE ++++++++++++++++++++++++++++++++++
        Attributes:
            xxx

        Returns:
            xxx
        '''
        self._cookie_check_and_click()

        # Initialising default dict and adding the passed ID and 
        # category parameters
        product_dict = dict()
        product_dict['ID'] = ID
        product_dict['Category'] = category

        # Getting the product page and parsing the html into bs4
        self.driver.get(product_url)
        sleep(1.5)
        homePage_html = self.driver.find_element_by_xpath('//*')
        homePage_html = homePage_html.get_attribute('innerHTML')
        homePage_soup = BeautifulSoup(homePage_html, 'lxml')

        # Getting data from page. Looped through multiple attempts 
        # to allow for errors due to elements not being loaded yet
        for i in range(self.BATCH_ATTEMPTS):
            try:
                # Product title (str)
                title = homePage_soup.find('h1').text
                product_dict['Title'] = title

                # Product Locaton (str)
                location = homePage_soup.find('span', {'class': '_pbq7fmm'}).text.replace(',', '')
                product_dict['Location'] = location

                # Counts for beds, bedrooms, beds and bathrooms (all int)
                info = self.string_clean(
                    homePage_soup.find('div', {'class': '_xcsyj0'}).next_sibling.text, 
                    str_type = 'info')
                for val in info:
                    product_dict[val[0]] = val[1]

                # Number of Reviews (int)
                review_count = self.string_clean(
                    homePage_soup.find('span', {'class': '_142pbzop'}).text, 
                    str_type = 'review count') 
                product_dict['Review_Count'] = review_count

                # Overall star rating (float)
                overall_rating = homePage_soup.find('span', {'class': '_1ne5r4rt'}).text
                product_dict['Overall Rate'] = overall_rating

                # Price per night (float)
                price_pNight = homePage_soup.find('span', {'class': '_tyxjp1'}).text[1:] # Gets rid of £
                product_dict['Price (Night)'] = price_pNight

                # Sub ratings (list of floats)
                subratings_container = homePage_soup.find('div', class_= 'ciubx2o dir dir-ltr')
                subratings = subratings_container.findChildren('div', recursive = False)
                for subrating in subratings:
                    if subrating.div.div.div.text:
                        product_dict[subrating.div.div.div.text + '_rate'] = \
                            subrating.div.div.div.nextSibling.text

                # How many amneties each location has (int)
                amenities_container = homePage_soup.find('div', class_ = 'b6xigss dir dir-ltr')
                amenities_count = self.string_clean(
                    amenities_container.a.text, 
                    str_type='amenities')
                product_dict['amenities_count'] = amenities_count

                # Product URL (str)
                product_dict['url'] = product_url
                break
            
            except:
                continue
        
        return product_dict


    def scrape_all(self, sample = False):
        '''
        The main function which utilises all other functions above to
        scrape all products from all headers when sample is False, 
        and scrapes the top 20 products from the first 3 headers (catrgories)
        when sample is set to True

        '''
        # Primary key, pandas dataframe and a missing data count initialised
        ID = 1000
        MISSING_DATA = 0
        self.df = pd.DataFrame()

        # Establishing parameters to the called functions that are dependant on the boolean condition of sample
        scroll = not sample
        to_count = 3 if sample else 25
        filename = 'products_sample.csv' if sample else 'products.csv'

        try: 
            # First, self.category_links and self.categories are populated by calling _get_categories()
            # with count parameter set to 3 if sample, else it is set to 25 (i.e. all)
            self._get_categories(count = to_count)

            # Iterating through each category yielded
            for category_no in range(len(self.categories)):
                # All product links are gathered into self.product_links. 
                # When a new category is iterated, self.product_links is reassigned with the new products 
                # For a sample, scrolling is locked so only top 20 products are accounted for
                self._get_products(self.category_links[category_no], SCROLLING=scroll)

                # Iterating over each product url in a category
                for prod_url in self.product_links:
                    try:
                        # Calling the scrape_product() function and logging data to the initialised pandas dataframe
                        product = self.scrape_product(prod_url, ID, self.categories[category_no])
                        self.df = self.df.append(product, ignore_index=True)
                        ID+=1
                    except:
                        # When a product page fails to give information, this is logged as missing data and doesn't break code
                        MISSING_DATA +=1
                        ID += 1
        finally:
            # Regardless of errors or interruptions, all yielded data is dumped into a csv
            self.df.to_csv(filename, index=False)



def main():
    scraper = Scraper()


if __name__ == '__main__':
    main()


###############################################################
# TO DO LIST:
    # Does this need any magic functions? Any more class/static functions?
    # Proxy to get round the 'too many requests'
    # Is it possible to make this faster?? Threading?
    # Docstring everything properly. Look at online examples
    # Make Test Files etc
    # Make the setup files

    

