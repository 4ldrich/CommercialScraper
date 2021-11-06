
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import pandas as pd
from time import sleep
import os


# TODO: Private bathroom! Need to parse this
look = 'https://www.airbnb.co.uk/rooms/39880406?category_tag=Tag%3A8186&adults=1&check_in=2021-12-12&check_out=2021-12-19&federated_search_id=98a9c936-7624-4e8d-9356-6bc305667f7a&source_impression_id=p3_1635279677_HneWU7t8%2F2vhed1n&guests=1'

class Scraper:
    """A Webscraper that crawls through Airbnb's website and gathers structured/unstructured data.

    Attributes
    ----------
    BATCH_ATTEMPTS : int
        It is common that a Scraper can fail to find an element on a webpage for numerous reasons,
        for example that the element hasn't been loaded yet. `BATCH_ATTEMPTS` allows for this and 
        offers 30 attempts for the Scraper to locate and pull data from each element it is looking 
        for, until the Scraper assumes that the element doesn't exist in the particular page.
    main_url : str
        The URL for Airbnb's home page, provided for the Selenium webdriver to get upon initialization
        of the Scraper object.
    driver : Selenium Webdriver
        The webdriver that is utilized to crawl through Airbnb's website

    """

    def __init__(self):
        """Initializes an instance of a Selenium Webdriver and navigates to the main product hub of Airbnb.

        When an instance of Scraper is initialized, a Selenium Webdriver gets the homepage by use
        of the `url` attribute. Then it clicks past the cookie wall (if applicable), and navigates onto
        the main products hub.
        """

        self.BATCH_ATTEMPTS = 30
        self.main_url = "https://www.airbnb.co.uk/"
        self.driver = None

        # Making destination paths for data to be stored
        os.mkdir('data')
        os.mkdir('data/alphanumeric')
        os.mkdir('data/images')

        # Initialising the selenium webdriver
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)


        # Getting the Airbnb url and clicking past the cookie wall
        self.driver.get(self.main_url)

        sleep(3)
        self._cookie_check_and_click()

        # Click the I'm flexible to get to the product browser 
        flexible_button = self.driver.find_element_by_link_text("I’m flexible")
        flexible_button.click()
        sleep(3)


    def get_categories(self, count = 25):
        """Gets category names and corresponding urls for each product header in Airbnb's main products page. 
        
        This method first clicks past a cookie wall if applicable. Using the `driver` that has been initialised
        with the Scraper object, this method located through and clicks each header button in the top menu bar of 
        the main products page. When each header is clicked, the category name and the current url of that clicked 
        header are stored into a zip object. 

        Parameters
        ----------
        count : int , optional
            When specified, the `count` parameter will set a limit to the number of headers that are clicked through
            and consequently, the number of categories and corresponding urls that are returned. This parameter is optional,
            and defaulted to 25 which is the number of total headers thatpopulate Airbnb's products page.
        
        Returns
        -------
        zip of tuples of (str, str)
            A zipped object of tuples of the category name, followed by the url of opening that header.
        
        """
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
        categories = []
        category_links = []
        for header in headers:
            categories.append(header.text)
        categories.remove('More')
        categories = categories[:count]

        print(categories)
        print(category_links)

        # Click through the visible headers to get urls for each one (except for 'More')
        counted = 0
        for i in range(len(headers)):
            headers[i].click()
            if i!= len(headers) - 1:
                category_links.append(self.driver.current_url)
                counted +=1
                # Break the entire function if count is met
                if counted == count:
                    return zip(categories, category_links)

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
                    categories.append(more_headers[j].text)
                    more_headers[j].click()
                    sleep(0.5)
                    # After clicking that header, get the corresponding header url for it
                    category_links.append(self.driver.current_url)
                    headers[i].click()
                    counted+=1
                    # Break the entire function if count is met
                    if counted == count:
                        return zip(categories, category_links)


    def __scroll(self, driver, SCROLL_PAUSE_TIME):
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                return
            last_height = new_height


    def get_products(self, header_url, SCROLLING = True):

        self.driver.get(header_url)
        sleep(0.5)
        self._cookie_check_and_click()
        self.driver.execute_script("document.body.style.zoom='75%'")
        sleep(3)

        # SCROLLING will 'lazy load' all ~300 objects per header tab
        # Set to FALSE when testing/sampling
        if SCROLLING:
            self.__scroll(self.driver, 4)

        for i in range(self.BATCH_ATTEMPTS):
            try:
                # After scrolling, Get HTML soup for whole page of 1 header
                homePage_html = self.driver.find_element_by_xpath('//*')
                homePage_html = homePage_html.get_attribute('innerHTML')
                homePage_soup = BeautifulSoup(homePage_html, 'html.parser')


                # Store all links for locations listed on page in array
                places_container = homePage_soup.find('div', class_ = '_ty2eq0')
                places = places_container.find_all('div', class_= '_1kmzzkf')
                product_links = np.array([])
                for place in places:
                    url = f"https://www.airbnb.co.uk{place.a['href']}"
                    product_links = np.append(product_links,url)
            except:
                pass
        return product_links


    def __is_cookie_button_present(self):
        # Returns true if cookie button is present, otherwise False
        # Used as boolean logic for _cookie_check_and_click()
        for i in range(10):
            try:
                return self.driver.find_element_by_class_name("_p76cpas") is not None
            except:
                pass
        return False


    def _cookie_check_and_click(self):
        # Checks if a cookie button is present using the method __is_cookie_button_present()
        # if there is one present, selenium driver will find and click it, else nothing happens
        # (no error can be thrown either way, and this covers the base of possible cookie problems)
        if self.__is_cookie_button_present():
            cookie_button= self.driver.find_element_by_class_name("_p76cpas")
            cookie_button.click()
            sleep(0.5)
            return True
        else:
            return False


    @staticmethod 
    def string_clean(text: str, str_type) -> str:


        if str_type == 'info':
            output = []
            # Organises the text into a clean list of 
            # ['x guests', 'x bedrooms', 'x beds', 'x bathrooms']
            # this is much easier to be iterated over and parsed
            text = text.replace('·', '')
            text = text.split('  ')
            clean_info = []
            for i in text:
                clean_info.append(i)
            
            for val in clean_info:
                label = val.split()[1]
                # unlikely to happen, but if theres an anomaly in the site text, 
                # the certain element is ignored and this doesn't mess up the data
                if label not in ['guests', 'guest', 'bedrooms', 'bedroom',
                    'beds', 'bed', 'bathrooms' ,'bathroom', 'private bathroom']:
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


    def __scrape_product_images(self, driver, ID):
        os.mkdir('data/images/'+ str(ID))


        sleep(0.33)
        homePage_html = driver.find_element_by_xpath('//*')
        homePage_html = homePage_html.get_attribute('innerHTML')
        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
        images = homePage_soup.find_all('img', class_='_6tbg2q')

        if images is None:
            raise Exception

        char_no = 97
        for image in images:
            image_src = image['src']
            urllib.request.urlretrieve(image_src,'data/images/' + str(ID) + '/' + str(ID) + chr(char_no) + '.png')
            char_no +=1


    def scrape_product_data(self, product_url, ID, category):

        self._cookie_check_and_click()

        # Initialising default dict and adding the passed ID and 
        # category parameters
        product_dict = dict()
        product_dict['ID'] = ID
        product_dict['Category'] = category

        # Getting the product page and parsing the html into bs4
        self.driver.get(product_url)
        sleep(0.33)

        for i in range(self.BATCH_ATTEMPTS):
            try:
                self.__scrape_product_images(self.driver, ID)
                break
            except:
                continue


        # Getting data from page. Looped through multiple attempts 
        # to allow for errors due to elements not being loaded yet
        for j in range(self.BATCH_ATTEMPTS):
            try:

                # Product title (str)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        homePage_html = self.driver.find_element_by_xpath('//*')
                        homePage_html = homePage_html.get_attribute('innerHTML')
                        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
                        title = homePage_soup.find('h1').text
                        product_dict['Title'] = title
                        break
                    except:
                        continue

                # Product Locaton (str)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        homePage_html = self.driver.find_element_by_xpath('//*')
                        homePage_html = homePage_html.get_attribute('innerHTML')
                        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
                        location = homePage_soup.find('span', {'class': '_pbq7fmm'}).text.replace(',', '')
                        product_dict['Location'] = location
                        break
                    except:
                        continue

                # Counts for beds, bedrooms, beds and bathrooms (all int)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        homePage_html = self.driver.find_element_by_xpath('//*')
                        homePage_html = homePage_html.get_attribute('innerHTML')
                        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
                        info = self.string_clean(
                            homePage_soup.find('div', {'class': '_xcsyj0'}).next_sibling.text, 
                            str_type = 'info')
                        for val in info:
                            product_dict[val[0]] = val[1]
                        break
                    except:
                        continue

                # Number of Reviews (int)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        homePage_html = self.driver.find_element_by_xpath('//*')
                        homePage_html = homePage_html.get_attribute('innerHTML')
                        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
                        review_count = self.string_clean(
                            homePage_soup.find('span', {'class': '_142pbzop'}).text, 
                            str_type = 'review count') 
                        product_dict['Review_Count'] = review_count
                        break
                    except:
                        continue

                # Overall star rating (float)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        homePage_html = self.driver.find_element_by_xpath('//*')
                        homePage_html = homePage_html.get_attribute('innerHTML')
                        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
                        overall_rating = homePage_soup.find('span', {'class': '_1ne5r4rt'}).text
                        product_dict['Overall_Rate'] = overall_rating
                        break
                    except:
                        continue

                # Price per night (float)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        homePage_html = self.driver.find_element_by_xpath('//*')
                        homePage_html = homePage_html.get_attribute('innerHTML')
                        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
                        price_pNight = homePage_soup.find('span', {'class': '_tyxjp1'}).text[1:] # Gets rid of £
                        product_dict['Price_Night'] = price_pNight
                        break
                    except:
                        continue

                # Sub ratings (list of floats)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        homePage_html = self.driver.find_element_by_xpath('//*')
                        homePage_html = homePage_html.get_attribute('innerHTML')
                        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
                        subratings_container = homePage_soup.find('div', class_= 'ciubx2o dir dir-ltr')

                        subratings = subratings_container.findChildren('div', recursive = False)
                        for subrating in subratings:
                            if subrating.div.div.div.text:
                                product_dict[subrating.div.div.div.text + '_rate'] = \
                                    subrating.div.div.div.nextSibling.text
                        break
                    except:
                        continue

                # How many amneties each location has (int)
                for i in range(self.BATCH_ATTEMPTS):
                    try:
                        homePage_html = self.driver.find_element_by_xpath('//*')
                        homePage_html = homePage_html.get_attribute('innerHTML')
                        homePage_soup = BeautifulSoup(homePage_html, 'lxml')
                        amenities_container = homePage_soup.find('div', class_ = 'b6xigss dir dir-ltr')
                        amenities_count = self.string_clean(
                            amenities_container.a.text, 
                            str_type='amenities')
                        product_dict['amenities_count'] = amenities_count
                        break
                    except:
                        continue

                # Product URL (str)
                product_dict['url'] = product_url

                # Catches if html hasn't been parsed properly due to loading lag, and re-runs the loop
                if  product_dict['Title'] == None \
                    or product_dict['Location'] == None\
                    or product_dict['url'] == None:
                    print('test')
                    sleep(0.1)
                    raise ValueError
                else:
                    break
            
            except:
 
                continue
        
        return product_dict


    def scrape_all(self, sample = False):

        # Primary key, pandas dataframe and a missing data count initialised
        ID = 1000
        self.df = pd.DataFrame()


        # Establishing parameters to the called functions that are dependant on the boolean condition of sample
        scroll = not sample
        to_count = 2 if sample else 25
        filename = 'products_sample.csv' if sample else 'products.csv'

        try: 
            # Getting the zipped object of header names and urls
            categories = self.get_categories(count = to_count)

            # Iterating through each category yielded
            for header, link in categories:
                # All product links are gathered into self.product_links. 
                # When a new category is iterated, self.product_links is reassigned with the new products 
                # For a sample, scrolling is locked so only top 20 products are accounted for
                links = self.get_products(link, SCROLLING=scroll)

                # Iterating over each product url in a category
                for prod_url in links:
                    try:
                        # Calling the scrape_product() function and logging data to the initialised pandas dataframe
                        product = self.scrape_product_data(prod_url, ID, header)
                        self.df = self.df.append(product, ignore_index=True)
                        ID+=1
                    except Exception as e:
                        # When a product page fails to give information, this is logged as missing data and doesn't break code
                        ID += 1
                        print(e)
        finally:
            # Regardless of errors or interruptions, all yielded data is dumped into a csv
            self.df.to_csv('data/alphanumeric/' + filename, index=False)



def main():
    scraper = Scraper()
    scraper.scrape_all()    

if __name__ == '__main__':
    main()


###############################################################
# TO DO LIST:
    # Does this need any magic functions? Any more class/static functions?
    # Is it possible to make this faster?? Threading?
    # Docstring everything properly. Look at online examples
    # Make Test Files etc
    # Make the setup files

    

